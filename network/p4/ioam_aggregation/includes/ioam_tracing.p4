control process_ioam_pto(inout headers hdr,
                             inout metadata meta,
                             inout standard_metadata_t standard_metadata) {

    action ioam_trace_node(){
        // node_data_field: | hop limit (8 Bit) | node id (24 Bit) |
        bit<(IOAM_PTO_DATA_LIST_LEN)> node_data_field = (bit<(IOAM_PTO_DATA_LIST_LEN)>) meta.ioamMeta.nodeID;

        // generate hop limit 32 bit mask --> 8 MSB set to the hop limit of IPv6 header at egress
        bit<(IOAM_PTO_DATA_LIST_LEN)> hop_limit_mask = (bit<(IOAM_PTO_DATA_LIST_LEN)>) (hdr.ipv6.hopLimit) << 24;

        // append the hop limit as the 8 MSB of the node data field
        node_data_field =  node_data_field | hop_limit_mask;

        // push data field to node data stack
        hdr.ioam_pto.dataList = hdr.ioam_pto.dataList << 32;
        hdr.ioam_pto.dataList = hdr.ioam_pto.dataList | node_data_field;

        // decrement remaining length
        hdr.ioam_pto.remainingLen = hdr.ioam_pto.remainingLen - 1;
    }

    apply {
        if (hdr.ioam_pto.isValid()) {
            if (hdr.ioam_pto.remainingLen > 0) {
                if (hdr.ioam_pto.namespaceID == meta.ioamMeta.namespaceID) {
                    // add node id and hop count to array
                    ioam_trace_node();
                }
            } else {
                // set overflow bit
                hdr.ioam_pto.flags = hdr.ioam_pto.flags | 0x8;
            }
        }
    }
}
