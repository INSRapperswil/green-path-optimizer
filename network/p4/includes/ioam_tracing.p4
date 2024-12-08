control process_ioam_tracing(inout headers hdr,
                             inout metadata meta,
                             inout standard_metadata_t standard_metadata) {

    action ioam_trace_node(){
        // node_data_field: | hop limit (8 Bit) | node id (24 Bit) |
        bit<(IOAM_TRACE_DATA_LIST_LEN)> node_data_field = (bit<(IOAM_TRACE_DATA_LIST_LEN)>) meta.ioamMeta.nodeID;

        // generate hop limit 32 bit mask --> 8 MSB set to the hop limit of IPv6 header at egress
        bit<(IOAM_TRACE_DATA_LIST_LEN)> hop_limit_mask = (bit<(IOAM_TRACE_DATA_LIST_LEN)>) (hdr.ipv6.hopLimit) << 24;

        // append the hop limit as the 8 MSB of the node data field
        node_data_field =  node_data_field | hop_limit_mask;

        // push data field to node data stack
        hdr.ioam_t_ioam_trace.dataList = hdr.ioam_t_ioam_trace.dataList << 32;
        hdr.ioam_t_ioam_trace.dataList = hdr.ioam_t_ioam_trace.dataList | node_data_field;

        // decrement remaining length
        hdr.ioam_t_ioam_trace.remainingLen = hdr.ioam_t_ioam_trace.remainingLen - 1;
    }

    apply {
        if (hdr.ioam_t_ioam_trace.isValid()) {
            if (hdr.ioam_t_ioam_trace.remainingLen > 0) {
                if (hdr.ioam_t_ioam_trace.namespaceID == meta.ioamMeta.namespaceID) {
                    // add node id and hop count to array
                    ioam_trace_node();
                }
            } else {
                // set overflow bit
                hdr.ioam_t_ioam_trace.flags = hdr.ioam_t_ioam_trace.flags | 0x8;
            }
        }
    }
}
