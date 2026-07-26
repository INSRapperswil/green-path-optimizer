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
            IPV6_NH_HOP_BY_HOP: parse_ipv6_hop_opt;
            default: accept;
        }
    }

    state parse_ipv6_hop_opt {
        packet.extract(hdr.ipv6_hop_opt);
        transition parse_ipv6_option_pto;
    }

    state parse_ipv6_option_pto {
        packet.extract(hdr.ipv6_option_pto);
        transition select(hdr.ipv6_option_pto.optionType) {
            HOP_BY_HOP_IOAM_OPTION: parse_ioam_option_pto;
        }
    }

    state parse_ioam_option_pto {
        packet.extract(hdr.ioam_option_pto);
        transition select(hdr.ioam_option_pto.ioamOptType) {
            IOAM_TRACE_PLUS_TEMPLATE_OPTION_TYPE: parse_ioam_pto;
        }
    }

    state parse_ioam_pto {
        packet.extract(hdr.ioam_pto);
        transition select(hdr.ioam_pto.templateID) {
            IOAM_AGGREGATION_TEMPLATE: parse_ioam_aggregation;
            default: accept;
        }
    }

    state parse_ioam_aggregation {
        packet.extract(hdr.ioam_aggregation);
        transition parse_ioam_pto_ndl;
    }

    state parse_ioam_pto_ndl {
        packet.extract(hdr.ioam_pto_ndl);
        transition parse_ipv6_option_padn;
    }

    state parse_ipv6_option_padn {
        packet.extract(hdr.ipv6_option_padn);
        transition select(hdr.ipv6_option_padn.optionDataLen) {
            0: accept;
            default: parse_padn;
        }
    }

    state parse_padn {
        packet.extract(hdr.padn);
        transition select(hdr.ipv6_hop_opt.nextHeader) {
            IPV6_NH_UDP: parse_udp;
            default: accept;
        }
    }

    state parse_udp {
        packet.extract(hdr.udp);
        transition accept;
    }
}
