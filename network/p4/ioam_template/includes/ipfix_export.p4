control process_ipfix_export(inout headers hdr,
                             inout metadata meta) {
    
    action perform_ipfix_export() {
        // Craft all the composed raw values using concatenation        
        flowKey_t flowKey = hdr.ipv6.flowLabel ++ hdr.ipv6.srcAddr;

        bit<320> ipv6_main_header = hdr.ipv6.version 
        ++ hdr.ipv6.trafficClass
        ++ hdr.ipv6.flowLabel
        ++ hdr.ipv6.payloadLen
        ++ hdr.ipv6.nextHeader
        ++ hdr.ipv6.hopLimit
        ++ hdr.ipv6.srcAddr
        ++ hdr.ipv6.dstAddr;
        
        bit<16> hop_by_hop_ext_header = hdr.ipv6_hop_opt.nextHeader
        ++ hdr.ipv6_hop_opt.hdrLen;

        bit<16> ipv6_option_header_ioam_pto = hdr.ipv6_option_pto.optionType
        ++ hdr.ipv6_option_pto.optionDataLen;

        bit<16> ioam_option_header_pto = hdr.ioam_option_pto.reserved
        ++ hdr.ioam_option_pto.ioamOptType;

        bit<192> ioam_pto_data = hdr.ioam_pto.namespaceID
        ++ hdr.ioam_pto.nodeLen
        ++ hdr.ioam_pto.flags
        ++ hdr.ioam_pto.remainingLen
        ++ hdr.ioam_pto.ioamTraceType
        ++ hdr.ioam_pto.reserved
        ++ hdr.ioam_pto.dataList;

        bit<16> ipv6_option_header_ioam_template = hdr.ipv6_option_template.optionType
        ++ hdr.ipv6_option_template.optionDataLen;

        bit<16> ioam_option_header_template  = hdr.ioam_option_template.reserved
        ++ hdr.ioam_option_template.ioamOptType;

        bit<32> ioam_header_template = hdr.ioam_template.namespaceID
        ++ hdr.ioam_template.templateID
        ++ hdr.ioam_template.length;

        bit<96> ioam_template_aggregation = hdr.ioam_aggregation.dataParam
        ++ hdr.ioam_aggregation.aggregator
        ++ hdr.ioam_aggregation.flags
        ++ hdr.ioam_aggregation.aggregate
        ++ hdr.ioam_aggregation.auxilDataNodeID
        ++ hdr.ioam_aggregation.hopCount;

        bit<16> ipv6_option_header_padn = hdr.ipv6_option_padn.optionType
        ++ hdr.ipv6_option_padn.optionDataLen;

        bit<32> padn_data = hdr.padn.padding;

        bit<768> raw_full_ipv6_header = ipv6_main_header
        ++ hop_by_hop_ext_header
        ++ ipv6_option_header_ioam_pto
        ++ ioam_option_header_pto
        ++ ioam_pto_data
        ++ ipv6_option_header_ioam_template
        ++ ioam_option_header_template
        ++ ioam_header_template
        ++ ioam_template_aggregation
        ++ ipv6_option_header_padn
        ++ padn_data;

        // Pass all values to control plane by calling the extern function
        ProcessEfficiencyIndicatorMetadata(
            meta.ioamMeta.nodeID,
            flowKey,
            hdr.ipv6.flowLabel,
            hdr.ipv6.srcAddr,
            hdr.ipv6.dstAddr,
            hdr.udp.srcPort,
            hdr.udp.dstPort,
            hdr.ioam_aggregation.dataParam,
            hdr.ioam_aggregation.aggregate,
            hdr.ioam_aggregation.aggregator,
            hdr.ioam_aggregation.flags,
            raw_full_ipv6_header);
    }
    apply {
        // Perform IPFIX export on last hop only
        if (hdr.ioam_aggregation.isValid() && meta.forwardingMeta.routeType == 0) {
            perform_ipfix_export();
        }
    }
}
