# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: p4/tmp/p4config.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x15p4/tmp/p4config.proto\x12\x06p4.tmp"\xce\x01\n\x0eP4DeviceConfig\x12\x10\n\x08reassign\x18\x01 \x01(\x08\x12-\n\x06\x65xtras\x18\x02 \x01(\x0b\x32\x1d.p4.tmp.P4DeviceConfig.Extras\x12\x13\n\x0b\x64\x65vice_data\x18\x03 \x01(\x0c\x1a\x66\n\x06\x45xtras\x12\x31\n\x02kv\x18\x01 \x03(\x0b\x32%.p4.tmp.P4DeviceConfig.Extras.KvEntry\x1a)\n\x07KvEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x02\x38\x01\x62\x06proto3'
)

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "p4.tmp.p4config_pb2", globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _P4DEVICECONFIG_EXTRAS_KVENTRY._options = None
    _P4DEVICECONFIG_EXTRAS_KVENTRY._serialized_options = b"8\001"
    _P4DEVICECONFIG._serialized_start = 34
    _P4DEVICECONFIG._serialized_end = 240
    _P4DEVICECONFIG_EXTRAS._serialized_start = 138
    _P4DEVICECONFIG_EXTRAS._serialized_end = 240
    _P4DEVICECONFIG_EXTRAS_KVENTRY._serialized_start = 199
    _P4DEVICECONFIG_EXTRAS_KVENTRY._serialized_end = 240
# @@protoc_insertion_point(module_scope)
