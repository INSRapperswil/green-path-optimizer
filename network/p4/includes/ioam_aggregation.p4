control process_ioam_aggregation(inout headers hdr,
                                     inout metadata meta,
                                     inout standard_metadata_t standard_metadata) {
    action set_flag(ioamFlag_t flag) {
        hdr.ioam_a_ioam_aggregation.flags = hdr.ioam_a_ioam_aggregation.flags | flag;
        hdr.ioam_a_ioam_aggregation.auxilDataNodeID = meta.ioamMeta.nodeID;
    }

    action ioam_aggr_sum() {
        // detect overflow
        if ((hdr.ioam_a_ioam_aggregation.aggregate + meta.ioamAggrMeta.aggregate) < hdr.ioam_a_ioam_aggregation.aggregate) {
            set_flag(IOAM_FLAG_OTHER_ERROR);
            return;
        }

        hdr.ioam_a_ioam_aggregation.hopCount = hdr.ioam_a_ioam_aggregation.hopCount + 1;
        hdr.ioam_a_ioam_aggregation.aggregate = hdr.ioam_a_ioam_aggregation.aggregate + meta.ioamAggrMeta.aggregate;
        hdr.ioam_a_ioam_aggregation.auxilDataNodeID = meta.ioamMeta.nodeID;
    }

    action ioam_aggr_min() {
        hdr.ioam_a_ioam_aggregation.hopCount = hdr.ioam_a_ioam_aggregation.hopCount + 1;
        if (hdr.ioam_a_ioam_aggregation.aggregate == 0 || hdr.ioam_a_ioam_aggregation.aggregate > meta.ioamAggrMeta.aggregate) {
            hdr.ioam_a_ioam_aggregation.aggregate = meta.ioamAggrMeta.aggregate;
            hdr.ioam_a_ioam_aggregation.auxilDataNodeID = meta.ioamMeta.nodeID;
        }
    }

    action ioam_aggr_max() {
        hdr.ioam_a_ioam_aggregation.hopCount = hdr.ioam_a_ioam_aggregation.hopCount + 1;
        if (hdr.ioam_a_ioam_aggregation.aggregate == 0 || hdr.ioam_a_ioam_aggregation.aggregate < meta.ioamAggrMeta.aggregate) {
            hdr.ioam_a_ioam_aggregation.aggregate = meta.ioamAggrMeta.aggregate;
            hdr.ioam_a_ioam_aggregation.auxilDataNodeID = meta.ioamMeta.nodeID;
        }
    }

    apply {
        if (hdr.ioam_a_ioam_aggregation.isValid() && hdr.ioam_a_ioam_aggregation.flags == 0 ) {
            if (hdr.ioam_a_ioam_aggregation.namespaceID != meta.ioamMeta.namespaceID) {
                set_flag(IOAM_FLAG_UNSUPPORTED_NAMESPACE);
            }
            if (meta.ioamAggrMeta.dataParamError == 1) {
                set_flag(IOAM_FLAG_UNSUPPORTED_DATA_PARAM);
            }
            if (meta.ioamAggrMeta.otherError == 1) {
                set_flag(IOAM_FLAG_OTHER_ERROR);
            }
            if (hdr.ioam_a_ioam_aggregation.flags == 0) {
                switch (hdr.ioam_a_ioam_aggregation.aggregator) {
                    IOAM_AGGREGATOR_SUM: {ioam_aggr_sum();}
                    IOAM_AGGREGATOR_MIN: {ioam_aggr_min();}
                    IOAM_AGGREGATOR_MAX: {ioam_aggr_max();}
                    default: {set_flag(IOAM_FLAG_UNSUPPORTED_AGGREGATOR);}
                }
            }
        }
    }
}
