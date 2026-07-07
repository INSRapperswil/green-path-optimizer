control process_ioam_init(inout headers hdr,
                                     inout metadata meta,
                                     inout standard_metadata_t standard_metadata) {

    action ioam_init_metadata() {
        meta.ioamAggregationMeta.dataParamError = 0;
        meta.ioamAggregationMeta.otherError = 0;

        // In case of multiple templates this can be set dynamically 
        // depending on bits in the IP header (e.g. last n bits in the checksum)
        meta.ioamAggregationMeta.paddingLength = AGGREGATION_PADDING;

        // IOAM Option header (2 Bytes) + Aggregation Option Header (16 Bytes) 
        meta.ioamAggregationMeta.optionLength = 2 + 16;
    }

    action indicate_other_error() {
        meta.ioamAggregationMeta.otherError = 1;
    }

    action ioam_get_namespace_id(ioamNamespace_t id) {
        meta.ioamMeta.namespaceID = id;
    }

    action ioam_get_node_id(ioamNodeID_t id) {
        meta.ioamMeta.nodeID = id;
    }

    action ioam_aggr_get_data_param(ioamDataParam_t data_param) {
        meta.ioamAggregationMeta.dataParam = data_param;
    }

    action init_ioam_aggregatorSelector() {
        meta.ioamAggregationMeta.aggregatorSelector = (bit<2>) hdr.ipv6.payloadLen & 0b11;
    }

    action init_ipv6_hop_opt() {
        // Set the added headers to be valid
        hdr.ipv6_hop_opt.setValid();  

        // 2 Bytes: Hop By Hop Option header fields (Next Header, Length)
        // 6 Bytes: All Option Header identifications (IOAM PTO, IOAM Template, PadN) each 2 Bytes 
        // Divided by 8 due to 8 octet alignment
        // Minus one because the first 8 octets are not included in the header length as per RFC8200
        hdr.ipv6_hop_opt.hdrLen = (2 + 6 + IOAM_PTO_OPTION_LEN + meta.ioamAggregationMeta.optionLength + meta.ioamAggregationMeta.paddingLength) / 8 - 1;
        
        // Initialize IPv6 Hop by Hop Extension Header
        hdr.ipv6_hop_opt.nextHeader = hdr.ipv6.nextHeader;

        // Add Hop by Hop extension header to linked list
        hdr.ipv6.nextHeader = IPV6_NH_HOP_BY_HOP;
        // The payload length is increased with the length indicated by the header length field in the Hop by Hop Option header in octets.
        hdr.ipv6.payloadLen = hdr.ipv6.payloadLen + ((bit<16>) hdr.ipv6_hop_opt.hdrLen + 1) * 8;
    }

    action ioam_pto_push() {
        // Set the added headers to be valid
        hdr.ipv6_option_pto.setValid();
        hdr.ioam_option_pto.setValid();
        hdr.ioam_pto.setValid();

        // Initialize Option
        hdr.ipv6_option_pto.optionType = HOP_BY_HOP_IOAM_OPTION;
        hdr.ipv6_option_pto.optionDataLen = IOAM_PTO_OPTION_LEN;

        // Initialize IOAM Header
        hdr.ioam_option_pto.reserved = 0;
        hdr.ioam_option_pto.ioamOptType = IOAM_PRE_ALLOC_TRACE_OPTION_TYPE;

        // Initialize IOAM Trace Option Type Header
        hdr.ioam_pto.namespaceID = meta.ioamMeta.namespaceID;
        hdr.ioam_pto.nodeLen = 1; // num of 4 octet units
        hdr.ioam_pto.flags = 0;
        hdr.ioam_pto.remainingLen = (bit<7>) IOAM_PTO_NUM_NODES; // num of 4 octet units
        hdr.ioam_pto.ioamTraceType = 0x800000; // MSB set to 1
        hdr.ioam_pto.reserved = 0;
        hdr.ioam_pto.dataList = 0;
    }

    action ioam_aggregation_push() {
        // Set the added headers to be valid
        hdr.ipv6_option_aggregation.setValid();
        hdr.ioam_option_aggregation.setValid();
        hdr.ioam_aggregation.setValid();
        hdr.ipv6_option_padn.setValid();
        hdr.padn.setValid();

        // Initialize Option
        hdr.ipv6_option_aggregation.optionType = HOP_BY_HOP_IOAM_OPTION;
        hdr.ipv6_option_aggregation.optionDataLen = meta.ioamAggregationMeta.optionLength;

        // Initialize IOAM Header
        hdr.ioam_option_aggregation.reserved = 0;
        hdr.ioam_option_aggregation.ioamOptType = IOAM_AGGREGATION_OPTION_TYPE;

        // Initialize IOAM Aggregation Type Header
        hdr.ioam_aggregation.namespaceID = meta.ioamMeta.namespaceID;
        hdr.ioam_aggregation.flags = 0;
        hdr.ioam_aggregation.reserved = 0;
        hdr.ioam_aggregation.dataParam = meta.ioamAggregationMeta.dataParam;
        hdr.ioam_aggregation.aggregate = 0;
        hdr.ioam_aggregation.auxilDataNodeID = 0;
        hdr.ioam_aggregation.hopCount = 0;

        // Set PadN Option add 4 Bytes padding
        hdr.ipv6_option_padn.optionType = 1;
        hdr.ipv6_option_padn.optionDataLen = meta.ioamAggregationMeta.paddingLength;
        hdr.padn.padding = 0;
    }

    action ioam_aggr_set_aggregator(ioamAggregator_t aggregator) {
        hdr.ioam_aggregation.aggregator = aggregator;
    }

    action ioam_aggr_fallback_default_aggregator() {
        hdr.ioam_aggregation.aggregator = IOAM_AGGREGATOR_DEFAULT;
    }

    // used to check if the node is an ingress node (route type = 0)
    action set_reverse_route_type(bit<8> route_type) {
        meta.forwardingMeta.reverseRouteType = route_type;
    }

    // used to set a non local route type --> in case of lookup failure the node is not considered an ingress node
    action set_default_reverse_route_type() {
        meta.forwardingMeta.reverseRouteType = 255;
    }

    table ioam_namespace_id {
        key = {
            hdr.ethernet.srcAddr: exact;
        }
        actions = {
            ioam_get_namespace_id;
            indicate_other_error;
        }
        size = 1;
    }

    table ioam_node_id {
        key = {
            hdr.ethernet.srcAddr: exact;
        }
        actions = {
            ioam_get_node_id;
            indicate_other_error;
        }
        size = 1;
    }

    table ioam_aggr_data_param {
        key = {
            hdr.ethernet.srcAddr: exact;
        }
        actions = {
            ioam_aggr_get_data_param;
            indicate_other_error;
        }
        size = 1;
    }

    table ioam_aggr_aggregator {
        key = {
            meta.ioamAggregationMeta.aggregatorSelector: exact;
        }
        actions = {
            ioam_aggr_set_aggregator;
            ioam_aggr_fallback_default_aggregator;
        }
        size = 4;
    }

    table ipv6_reverse_lookup {
        key = {
            hdr.ipv6.srcAddr: lpm;
        }
        actions = {
            set_reverse_route_type;
            set_default_reverse_route_type;
        }
        size = 1024;
        default_action = set_default_reverse_route_type();
    }
    
    apply {
        // Initialize IOAM metadata
        ioam_init_metadata();
        ioam_namespace_id.apply();
        ioam_node_id.apply();
        ioam_aggr_data_param.apply();
        ipv6_reverse_lookup.apply();

        // Initialize IOAM
        if (!hdr.ipv6_hop_opt.isValid() && meta.ioamAggregationMeta.otherError == 0 && meta.forwardingMeta.reverseRouteType == 0) {
            init_ioam_aggregatorSelector();
            init_ipv6_hop_opt();
            ioam_pto_push();
            ioam_aggregation_push();
            ioam_aggr_aggregator.apply();
        }
    }
}
