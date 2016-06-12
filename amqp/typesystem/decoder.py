import datetime
import struct
import uuid

from amqp.typesystem import const
from amqp.utils import compat


def decode_null(format_code, value):
    assert value == b''
    return None


def decode_string(encoding, format_code, value):
    return value.decode(encoding)


def decode_integer(signed, format_code, value):
    return compat.from_bytes(value, 'big', signed=signed)


def decode_ieee_754_binary(length, format_code, value):
    assert length in (32, 64)
    return struct.unpack('!' + ('f' if (length == 32) else 'd'), value)[0]


def decode_boolean(format_code, value):
    return (format_code == const.TRUE)\
        or (compat.from_bytes(value, 'big') == 1)


def decode_binary(format_code, value):
    return value


def decode_timestamp(format_code, value):
    # The AMQP timestamp datatype is a signed long integer representing the
    # number of milliseconds since the UNIX epoch.
    timestamp = (float if compat.PY2 else lambda x: x)\
        (decode_integer(True, const.LONG, value)) / 1000
    return datetime.datetime.utcfromtimestamp(timestamp)


def decode_uuid(format_code, value):
    return uuid.UUID(bytes=value)
