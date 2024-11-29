/*************************************************************************
*********************** P A R S E R  ***********************************
*************************************************************************/

parser MyParser(packet_in packet,
                out headers hdr,
                inout metadata meta,
                inout standard_metadata_t standard_metadata) {

    state start {
        transition parse_ethernet;
    }

    state parse_ethernet {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            TYPE_IPV4: parse_ipv4;
            TYPE_IPV6: parse_ipv6;
            default: accept;
        }
    }

    state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition accept;
    }

    state parse_ipv6 {
        packet.extract(hdr.ipv6);
        transition select(hdr.ipv6.nextHeader) {
            IPV6_NH_HOP_BY_HOP: parse_ipv6_ioam_t_ext_hop_by_hop;
            IPV6_NH_UDP: parse_udp;
            default: accept;
        }
    }

    state parse_ipv6_ioam_t_ext_hop_by_hop {
        packet.extract(hdr.ipv6_ext_hop_by_hop);
        transition parse_ioam_t_ipv6_option;
    }

    state parse_ioam_t_ipv6_option {
        packet.extract(hdr.ioam_t_ipv6_option);
        transition select(hdr.ioam_t_ipv6_option.optionType) {
            IOAM_OPTION_TYPE_CHG: parse_ioam_t_ioam;
            default: accept;
        }
    }

    state parse_ioam_t_ioam {
        packet.extract(hdr.ioam_t_ioam);
        transition select(hdr.ioam_t_ioam.ioamOptType) {
            IOAM_PRE_ALLOC_TRACE_OPTION_TYPE: parse_ioam_t_ioam_trace;
            default: accept;
        }
    }

    state parse_ioam_t_ioam_trace {
        packet.extract(hdr.ioam_t_ioam_trace);
        transition parse_ioam_a_ipv6_option;
    }

    state parse_ioam_a_ipv6_option {
        packet.extract(hdr.ioam_a_ipv6_option);
        transition select(hdr.ioam_a_ipv6_option.optionType) {
            IOAM_OPTION_TYPE_CHG: parse_ioam_a_ioam;
            default: accept;
        }
    }

    state parse_ioam_a_ioam {
        packet.extract(hdr.ioam_a_ioam);
        transition select(hdr.ioam_a_ioam.ioamOptType) {
            IOAM_AGGREGATION_OPTION_TYPE: parse_ioam_a_ioam_aggregation;
            default: accept;
        }
    }

    state parse_ioam_a_ioam_aggregation {
        packet.extract(hdr.ioam_a_ioam_aggregation);
        transition parse_padn_ipv6_option;
    }

    state parse_padn_ipv6_option {
        packet.extract(hdr.option_padn);
        transition parse_padn_data;
    }

    state parse_padn_data {
        packet.extract(hdr.option_padn_data);
        transition select(hdr.ipv6_ext_hop_by_hop.nextHeader) {
            IPV6_NH_UDP: parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }
}
