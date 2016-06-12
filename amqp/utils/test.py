import datetime
import struct
import sys
import uuid


bytes = (lambda value=None: ''.join([struct.pack('!B', x) for x in value])\
    if value is not None else '') if (sys.version_info.major == 2)\
    else bytes


class DataTypesMixin(object):
    p_ubyte = 1
    b_ubyte = bytes([1])

    p_ushort = 256
    b_ushort = bytes([1,0])

    p_uint = 16777216
    b_uint = bytes([1,0,0,0])

    p_uint0 = 0
    b_uint0 = bytes()

    p_smalluint = 1
    b_smalluint = bytes([1])

    p_ulong = 72057594037927936
    b_ulong = bytes([1,0,0,0,0,0,0,0])

    p_ulong0 = 0
    b_ulong0 = bytes()

    p_smallulong = 1
    b_smallulong = bytes([1])

    p_byte = -1
    b_byte = bytes([255])

    p_short = -256
    b_short = bytes([255,0])

    p_int = -16777216
    b_int = bytes([255,0,0,0])

    p_smallint = -1
    b_smallint = bytes([255])

    p_long = -72057594037927936
    b_long = bytes([255,0,0,0,0,0,0,0])

    p_smalllong = -1
    b_smalllong = bytes([255])


    p_unix = datetime.datetime(1970, 1, 1)
    b_unix = bytes([0,0,0,0,0,0,0,0])

    p_gregorian = datetime.datetime(1, 1, 1)
    b_gregorian = bytes([255, 255, 199, 124, 237, 211, 40, 0])

    p_j2000 = datetime.datetime(2000, 1, 1)
    b_j2000 = bytes([0, 0, 0, 220, 106, 207, 172, 0])

    p_uuid4 = uuid.UUID('ce8e02d0-cb6c-466a-b8df-d834f1793144')
    b_uuid4 = bytes([206, 142, 2, 208, 203, 108, 70,
        106, 184, 223, 216, 52, 241, 121, 49, 68])

    p_float = 1.0
    b_float = bytes([63, 128, 0, 0])

    p_double = 1.0
    b_double = bytes([63, 240, 0, 0, 0, 0, 0, 0])

    b_sym8 = bytes([102, 111, 111]) # foo
    b_sym32 = bytes(102 for x in range(256))
    b_str8 = bytes([195, 171])
    b_str32 = bytes([195, 171] * 256)
    b_vbin8 = bytes([255,255])
    b_vbin32 = bytes([255,255,255])
