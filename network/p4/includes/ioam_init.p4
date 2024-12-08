control process_ioam_init(inout headers hdr,
                                     inout metadata meta,
                                     inout standard_metadata_t standard_metadata) {

    action ioam_init_metadata() {
        meta.ioamAggrMeta.dataParamError = 0;
        meta.ioamAggrMeta.otherError = 0;
    }

    action indicate_other_error() {
        meta.ioamAggrMeta.otherError = 1;
    }

    action ioam_get_namespace_id(ioamNamespace_t id) {
        meta.ioamMeta.namespaceID = id;
    }

    action ioam_get_node_id(ioamNodeID_t id) {
        meta.ioamMeta.nodeID = id;
    }

    action ioam_aggr_get_data_param(ioamDataParam_t data_param) {
        meta.ioamAggrMeta.dataParam = data_param;
    }

    action init_ioam_aggregator_selector() {
        meta.ioamAggrMeta.aggregator_selector = (bit<2>) hdr.ipv6.payloadLen & 0b11;
    }

    action init_ipv6_ext_hop_by_hop() {
        // Set the added headers to be valid
        hdr.ipv6_ext_hop_by_hop.setValid();

        // Initialize IPv6 Hop by Hop Extension Header
        hdr.ipv6_ext_hop_by_hop.nextHeader = hdr.ipv6.nextHeader;
        hdr.ipv6_ext_hop_by_hop.hdrLen = 1 + IOAM_TRACE_NUM_NODES / 2 + 3; // 1 octet unit for the header metadata + num nodes / 2 (1 node entry requires 4 octet units) + 3 octet units for IOAM Aggregation

        // Add Hop by Hop extension header to linked list
        hdr.ipv6.nextHeader = IPV6_NH_HOP_BY_HOP;
        hdr.ipv6.payloadLen = hdr.ipv6.payloadLen + 16 + (bit<16>) IOAM_TRACE_NUM_NODES * 4 + 24; // current payload + IOAM metadata + node data list length + IOAM Aggregation Data (18 Byte) + 6 Byte Padding
    }

    action ioam_trace_push() {
        hdr.ioam_t_ipv6_option.setValid();
        hdr.ioam_t_ioam.setValid();
        hdr.ioam_t_ioam_trace.setValid();

        // Initialize Option
        hdr.ioam_t_ipv6_option.optionType = IOAM_OPTION_TYPE_CHG;
        hdr.ioam_t_ipv6_option.optionDataLen = IOAM_TRACE_OPTION_DATA_LEN;

        // Initialize IOAM Header
        hdr.ioam_t_ioam.reserved = 0;
        hdr.ioam_t_ioam.ioamOptType = IOAM_PRE_ALLOC_TRACE_OPTION_TYPE;

        // Initialize IOAM Trace Option Type Header
        hdr.ioam_t_ioam_trace.namespaceID = meta.ioamMeta.namespaceID;
        hdr.ioam_t_ioam_trace.nodeLen = 1; // num of 4 octet units
        hdr.ioam_t_ioam_trace.flags = 0;
        hdr.ioam_t_ioam_trace.remainingLen = (bit<7>) IOAM_TRACE_NUM_NODES; // num of 4 octet units
        hdr.ioam_t_ioam_trace.ioamTraceType = 0x800000; // MSB set to 1
        hdr.ioam_t_ioam_trace.reserved = 0;
        hdr.ioam_t_ioam_trace.dataList = 0;
    }

    action ioam_aggr_push() {
        // Set the added headers to be valid
        hdr.ioam_a_ipv6_option.setValid();
        hdr.ioam_a_ioam.setValid();
        hdr.ioam_a_ioam_aggregation.setValid();
        hdr.option_padn.setValid();
        hdr.option_padn_data.setValid();

        // Initialize Option
        hdr.ioam_a_ipv6_option.optionType = IOAM_OPTION_TYPE_CHG;
        hdr.ioam_a_ipv6_option.optionDataLen = IOAM_AGGREGATION_OPTION_DATA_LEN;

        // Initialize IOAM Header
        hdr.ioam_a_ioam.reserved = 0;
        hdr.ioam_a_ioam.ioamOptType = IOAM_AGGREGATION_OPTION_TYPE;

        // Initialize IOAM Aggregation Type Header
        hdr.ioam_a_ioam_aggregation.namespaceID = meta.ioamMeta.namespaceID;
        hdr.ioam_a_ioam_aggregation.flags = 0;
        hdr.ioam_a_ioam_aggregation.reserved = 0;
        hdr.ioam_a_ioam_aggregation.dataParam = meta.ioamAggrMeta.dataParam;
        hdr.ioam_a_ioam_aggregation.aggregate = 0;
        hdr.ioam_a_ioam_aggregation.auxilDataNodeID = 0;
        hdr.ioam_a_ioam_aggregation.hopCount = 0;

        // Set PadN Option add 4 Bytes padding
        hdr.option_padn.optionType = 1;
        hdr.option_padn.optionDataLen = IPV6_EXT_HOP_BY_HOP_PADDING - 2; // N - 2 | N=2 => 0
        hdr.option_padn_data.padding = 0;
    }

    action ioam_aggr_set_aggregator(ioamAggregator_t aggregator) {
        hdr.ioam_a_ioam_aggregation.aggregator = aggregator;
    }

    action ioam_aggr_fallback_default_aggregator() {
        hdr.ioam_a_ioam_aggregation.aggregator = IOAM_AGGREGATOR_DEFAULT;
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
            meta.ioamAggrMeta.aggregator_selector: exact;
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
        if (!hdr.ipv6_ext_hop_by_hop.isValid() && meta.ioamAggrMeta.otherError == 0 && meta.forwardingMeta.reverseRouteType == 0) {
            init_ioam_aggregator_selector();
            init_ipv6_ext_hop_by_hop();
            ioam_trace_push();
            ioam_aggr_push();
            ioam_aggr_aggregator.apply();
        }
    }
}
