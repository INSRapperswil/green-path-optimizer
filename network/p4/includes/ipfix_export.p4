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
        
        bit<16> hop_by_hop_ext_header = hdr.ipv6_ext_hop_by_hop.nextHeader
        ++ hdr.ipv6_ext_hop_by_hop.hdrLen;

        bit<16> ipv6_option_header_ioam_trace = hdr.ioam_t_ipv6_option.optionType
        ++ hdr.ioam_t_ipv6_option.optionDataLen;

        bit<16> ioam_trace_header = hdr.ioam_t_ioam.reserved
        ++ hdr.ioam_t_ioam.ioamOptType;

        bit<192> ioam_trace_data = hdr.ioam_t_ioam_trace.namespaceID
        ++ hdr.ioam_t_ioam_trace.nodeLen
        ++ hdr.ioam_t_ioam_trace.flags
        ++ hdr.ioam_t_ioam_trace.remainingLen
        ++ hdr.ioam_t_ioam_trace.ioamTraceType
        ++ hdr.ioam_t_ioam_trace.reserved
        ++ hdr.ioam_t_ioam_trace.dataList;

        bit<16> ipv6_option_header_ioam_aggregation = hdr.ioam_a_ipv6_option.optionType
        ++ hdr.ioam_a_ipv6_option.optionDataLen;

        bit<16> ioam_aggregation_header = hdr.ioam_a_ioam.reserved
        ++ hdr.ioam_a_ioam.ioamOptType;

        bit<128> ioam_aggregation_data = hdr.ioam_a_ioam_aggregation.namespaceID
        ++ hdr.ioam_a_ioam_aggregation.flags
        ++ hdr.ioam_a_ioam_aggregation.reserved
        ++ hdr.ioam_a_ioam_aggregation.dataParam
        ++ hdr.ioam_a_ioam_aggregation.aggregator
        ++ hdr.ioam_a_ioam_aggregation.aggregate
        ++ hdr.ioam_a_ioam_aggregation.auxilDataNodeID
        ++ hdr.ioam_a_ioam_aggregation.hopCount;

        bit<16> ipv6_option_header_padn = hdr.option_padn.optionType
        ++ hdr.option_padn.optionDataLen;

        bit<32> padn_data = hdr.option_padn_data.padding;

        bit<768> raw_full_ipv6_header = ipv6_main_header
        ++ hop_by_hop_ext_header
        ++ ipv6_option_header_ioam_trace
        ++ ioam_trace_header
        ++ ioam_trace_data
        ++ ipv6_option_header_ioam_aggregation
        ++ ioam_aggregation_header
        ++ ioam_aggregation_data
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
            hdr.ioam_a_ioam_aggregation.dataParam,
            hdr.ioam_a_ioam_aggregation.aggregate,
            hdr.ioam_a_ioam_aggregation.aggregator,
            hdr.ioam_a_ioam_aggregation.flags,
            raw_full_ipv6_header);
    }
    apply {
        // Perform IPFIX export on last hop only
        if (hdr.ioam_a_ioam_aggregation.isValid() && meta.forwardingMeta.routeType == 0) {
            perform_ipfix_export();
        }
    }
}
