/*************************************************************************
*********************** CONSTANTS  ***************************************
*************************************************************************/

// EtherTypes
const bit<16> TYPE_IPV4 = 0x800;
const bit<16> TYPE_IPV6 = 0x86DD;

// IPv6 Next Header Types
const bit<8> IPV6_NH_HOP_BY_HOP = 0x0;
const bit<8> IPV6_NH_UDP = 0x11;

// Hop by Hop Extension Header Option Types
const bit<8> HOP_BY_HOP_IOAM_OPTION = 0x31;

// IOAM Option Types
const bit<8> IOAM_PRE_ALLOC_TRACE_OPTION_TYPE = 0x0;
const bit<8> IOAM_TEMPLATE_OPTION_TYPE = 0x5;

// IOAM Template Option Templates
const bit<8> IOAM_AGGREGATION_TEMPLATE = 0x1;
const bit<8> IOAM_AGGREGATION_TEMPLATE_LENGTH = 3; // Number of 4-octett units


const bit<8> IOAM_PTO_NUM_NODES = 4; // Must be an even number (if odd the padding must be adjusted appropriately)
const bit<8> IOAM_PTO_DATA_LIST_LEN = IOAM_PTO_NUM_NODES * 32; // Length in bits

// IOAM Option Data Size (1 Byte IOAM Opt-Type + 1 Byte Reserved + 8 Byte IOAM Trace Option Header + IOAM_PTO_NUM_NODES * 4 Byte)
const bit<8> IOAM_PTO_OPTION_LEN = 10 + IOAM_PTO_NUM_NODES * 4;


// IOAM Aggregators
const bit<8> IOAM_AGGREGATOR_SUM = 0x1;
const bit<8> IOAM_AGGREGATOR_MIN = 0x2;
const bit<8> IOAM_AGGREGATOR_MAX = 0x4;
const bit<8> IOAM_AGGREGATOR_DEFAULT = IOAM_AGGREGATOR_SUM;


// IOAM_FLAGS
const bit<8> IOAM_FLAG_UNSUPPORTED_AGGREGATOR = 0b00000001;
const bit<8> IOAM_FLAG_UNSUPPORTED_DATA_PARAM = 0b00000010;
const bit<8> IOAM_FLAG_UNSUPPORTED_NAMESPACE = 0b00000100;
const bit<8> IOAM_FLAG_OTHER_ERROR = 0b00001000;

// Padding
const bit<8> AGGREGATION_PADDING = 4; // With even length of node data list
// const bit<8> AGGREGATION_PADDING = 2; // With odd length of node data list