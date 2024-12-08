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
const bit<8> IOAM_OPTION_TYPE_CHG = 0x31;

// IOAM Aggregation Option Type Identifier (Not yet defined by IANA)
const bit<8> IOAM_PRE_ALLOC_TRACE_OPTION_TYPE = 0x0;
const bit<8> IOAM_AGGREGATION_OPTION_TYPE = 0x20;

// IOAM Option Data Size (1 Byte IOAM Opt-Type + 1 Byte Reserved + 16 Byte IOAM Aggregation Option)
const bit<8> IOAM_AGGREGATION_OPTION_DATA_LEN = 18;

const bit<8> IOAM_TRACE_NUM_NODES = 4; // Must be an even number (if odd the padding must be adjusted appropriately)
const bit<8> IOAM_TRACE_DATA_LIST_LEN = IOAM_TRACE_NUM_NODES * 32;
// IOAM Option Data Size (1 Byte IOAM Opt-Type + 1 Byte Reserved + 8 Byte IOAM Trace Option Header + IOAM_TRACE_NUM_NODES * 4 Byte)
const bit<8> IOAM_TRACE_OPTION_DATA_LEN = 10 + IOAM_TRACE_NUM_NODES * 4;

// IOAM Aggregators
const bit<8> IOAM_AGGREGATOR_SUM = 0x1;
const bit<8> IOAM_AGGREGATOR_MIN = 0x2;
const bit<8> IOAM_AGGREGATOR_MAX = 0x4;
const bit<8> IOAM_AGGREGATOR_AVG = 0x8;
const bit<8> IOAM_AGGREGATOR_DEFAULT = IOAM_AGGREGATOR_SUM;


// IOAM_FLAGS
const bit<4> IOAM_FLAG_UNSUPPORTED_AGGREGATOR = 0b0001;
const bit<4> IOAM_FLAG_UNSUPPORTED_DATA_PARAM = 0b0010;
const bit<4> IOAM_FLAG_UNSUPPORTED_NAMESPACE = 0b0100;
const bit<4> IOAM_FLAG_OTHER_ERROR = 0b1000;

// Padding
const bit<8> IPV6_EXT_HOP_BY_HOP_PADDING = 6;

// Efficiency Indicator
const bit<15> MAX_VALUE_15_BIT = 32767;
