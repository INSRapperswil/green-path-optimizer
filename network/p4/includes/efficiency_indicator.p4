/*************************************************************************
***************** E F F I C I E N C Y  I N D I C A T O R  ****************
*************************************************************************/

control process_efficiency_indicator(inout headers hdr,
                                     inout metadata meta,
                                     inout standard_metadata_t standard_metadata) {

    action add_indicator_to_aggregate(ioamAggregate_t indicator_value) {
        meta.ioamAggrMeta.aggregate = meta.ioamAggrMeta.aggregate + indicator_value;
    }

    action indicate_data_param_error() {
        meta.ioamAggrMeta.dataParamError = 1;
    }

    action indicate_other_error() {
        meta.ioamAggrMeta.otherError = 1;
    }

    table get_hop_efficiency_indicator {
        key = {
            hdr.ioam_a_ioam_aggregation.dataParam: exact;
        }
        actions = {
            add_indicator_to_aggregate;
            indicate_data_param_error;
        }
        size = 10;
    }

    table get_ingress_link_efficiency_indicator {
        key = {
            standard_metadata.ingress_port: exact;
        }
        actions = {
            add_indicator_to_aggregate;
            indicate_other_error;
        }
        size = 10;
    }

    table get_egress_link_efficiency_indicator {
        key = {
            standard_metadata.egress_port: exact;
        }
        actions = {
            add_indicator_to_aggregate;
            indicate_other_error;
        }
        size = 10;
    }

    apply {
        // Efficiency Indicator Processing
        if (hdr.ioam_a_ioam_aggregation.isValid() && hdr.ioam_a_ioam_aggregation.flags == 0) {
            get_hop_efficiency_indicator.apply();
            if (meta.ioamAggrMeta.dataParamError == 0) {
                get_ingress_link_efficiency_indicator.apply();
                get_egress_link_efficiency_indicator.apply();
            }
        }
    }
}
