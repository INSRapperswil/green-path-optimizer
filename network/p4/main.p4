/* -*- P4_16 -*- */
#include <core.p4>
#include <v1model.p4>
#include "includes/constants.p4"
#include "includes/types.p4"
#include "includes/headers.p4"
#include "includes/parser.p4"
#include "includes/externs.p4"
#include "includes/ioam_init.p4"
#include "includes/ioam_tracing.p4"
#include "includes/ioam_aggregation.p4"
#include "includes/efficiency_indicator.p4"
#include "includes/ipfix_export.p4"

/*************************************************************************
************   C H E C K S U M    V E R I F I C A T I O N   *************
*************************************************************************/

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}


/*************************************************************************
**************  I N G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata) {
    action drop() {
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(macAddr_t mac, egressSpec_t port, bit<8> route_type) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = mac;
        hdr.ipv4.ttl = hdr.ipv4.ttl - 1;
        meta.forwardingMeta.routeType = route_type;
    }

    action ipv6_forward(macAddr_t mac, egressSpec_t port, bit<8> route_type) {
        standard_metadata.egress_spec = port;
        hdr.ethernet.srcAddr = hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr = mac;
        hdr.ipv6.hopLimit = hdr.ipv6.hopLimit - 1;
        meta.forwardingMeta.routeType = route_type;
    }

    table ipv4_lpm {
        key = {
            hdr.ipv4.dstAddr: lpm;
        }
        actions = {
            ipv4_forward;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    table ipv6_lpm {
        key = {
            hdr.ipv6.dstAddr: lpm;
        }
        actions = {
            ipv6_forward;
            drop;
        }
        size = 1024;
        default_action = drop();
    }

    apply {
        // IP Forwarding
        if (hdr.ipv4.isValid()) {
            ipv4_lpm.apply();
        }
        if (hdr.ipv6.isValid()) {
            ipv6_lpm.apply();
        }
    }
}

/*************************************************************************
****************  E G R E S S   P R O C E S S I N G   *******************
*************************************************************************/

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata) {

    apply {
        if (hdr.ipv6.isValid()) {
            // Initialize IOAM protocol related header in IPv6 extension header
            process_ioam_init.apply(hdr, meta, standard_metadata);

            // IOAM Tracing
            process_ioam_tracing.apply(hdr, meta, standard_metadata);

            // Efficiency Indicator
            process_efficiency_indicator.apply(hdr, meta, standard_metadata);

            // IOAM Aggregation
            process_ioam_aggregation.apply(hdr, meta, standard_metadata);

            // IPFIX Export
            process_ipfix_export.apply(hdr, meta);
        }
    }
}

/*************************************************************************
*************   C H E C K S U M    C O M P U T A T I O N   **************
*************************************************************************/

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        update_checksum(
        hdr.ipv4.isValid(),
            { hdr.ipv4.version,
              hdr.ipv4.ihl,
              hdr.ipv4.diffserv,
              hdr.ipv4.totalLen,
              hdr.ipv4.identification,
              hdr.ipv4.flags,
              hdr.ipv4.fragOffset,
              hdr.ipv4.ttl,
              hdr.ipv4.protocol,
              hdr.ipv4.srcAddr,
              hdr.ipv4.dstAddr },
            hdr.ipv4.hdrChecksum,
            HashAlgorithm.csum16);
    }
}

/*************************************************************************
***********************  D E P A R S E R  *******************************
*************************************************************************/

control MyDeparser(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.ipv6);
        packet.emit(hdr.ipv6_ext_hop_by_hop);
        packet.emit(hdr.ioam_t_ipv6_option);
        packet.emit(hdr.ioam_t_ioam);
        packet.emit(hdr.ioam_t_ioam_trace);
        packet.emit(hdr.ioam_a_ipv6_option);
        packet.emit(hdr.ioam_a_ioam);
        packet.emit(hdr.ioam_a_ioam_aggregation);
        packet.emit(hdr.option_padn);
        packet.emit(hdr.option_padn_data);
        packet.emit(hdr.udp);
    }
}

/*************************************************************************
***********************  S W I T C H  *******************************
*************************************************************************/

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;
