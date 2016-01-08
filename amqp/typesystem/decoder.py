import collections
import functools
import operator
import struct
import uuid

from amqp.exc import DecodeError
from amqp.typesystem import const
from amqp.typesystem import basetypes
from amqp.typesystem.registry import get_by_constructor
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


def decode_uuid(format_code, value):
    return uuid.UUID(bytes=value)


class RawDecoder(object):
    __decoders = {
        const.NULL      : decode_null,
        const.BOOLEAN   : decode_boolean,
        const.TRUE      : decode_boolean,
        const.FALSE     : decode_boolean,
        const.BYTE      : functools.partial(decode_integer, True),
        const.SHORT     : functools.partial(decode_integer, True),
        const.INT       : functools.partial(decode_integer, True),
        const.SMALLINT  : functools.partial(decode_integer, True),
        const.LONG      : functools.partial(decode_integer, True),
        const.SMALLLONG : functools.partial(decode_integer, True),
        const.UBYTE     : functools.partial(decode_integer, False),
        const.USHORT    : functools.partial(decode_integer, False),
        const.UINT      : functools.partial(decode_integer, False),
        const.UINT0     : functools.partial(decode_integer, False),
        const.SMALLUINT : functools.partial(decode_integer, False),
        const.ULONG     : functools.partial(decode_integer, False),
        const.ULONG0    : functools.partial(decode_integer, False),
        const.SMALLULONG: functools.partial(decode_integer, False),
        const.FLOAT     : functools.partial(decode_ieee_754_binary, 32),
        const.DOUBLE    : functools.partial(decode_ieee_754_binary, 64),
        const.CHAR      : functools.partial(decode_string, 'utf-32-be'),
        const.MS64      : functools.partial(decode_integer, True),
        const.UUID      : decode_uuid,
        const.VBIN32    : decode_binary,
        const.VBIN8     : decode_binary,
        const.STR8      : functools.partial(decode_string, 'utf-8'),
        const.STR32     : functools.partial(decode_string, 'utf-8'),
        const.SYM8      : functools.partial(decode_string, 'ascii'),
        const.SYM32     : functools.partial(decode_string, 'ascii'),
    }
    __encodables = collections.defaultdict(lambda: basetypes.Scalar, {
        'null'  : basetypes.Null,
        'list'  : basetypes.List,
        'array' : basetypes.Array,
        'map'   : basetypes.Map
    })

    @classmethod
    def decode(cls, format_code, raw_value):
        """Decodes a byte-sequence holding an AMQP-encoded value using
        the given `format_code`.
        """
        if format_code not in cls.__decoders:
            raise DecodeError(format_code, raw_value)
        return cls.__decoders[format_code](format_code, raw_value)

    def __init__(self, buf):
        self.buf = buf
        self.current = None

    def value_from_node(self, node):
        """Extract the AMQP-encoded value from the buffer and coerce it to the
        appropriate Python object, based on the format code.
        """
        value = self.decode(node.format_code, node.value_from_buf(self.buf))
        return self.encodable_factory(node, value)

    def visit(self, node):
        return self.visit_scalar(node)\
            if node.is_scalar()\
            else self.visit_collection(node)

    def visit_scalar(self, node):
        """Visit a node representing a scalar value."""
        return self.value_from_node(node)

    def visit_collection(self, node):
        """Visit a :class:`.Node` representing a collection type."""
        assert any([node.is_list(), node.is_map(), node.is_array()])
        value = self.encodable_factory(node, [x.accept(self) for x in node])
        return value

    def encodable_factory(self, node, value):
        """Return the appropriate :class:`.Encodable` instance for the given
        :class:`.Node` `node`.
        """
        ti = node.type_identifier
        Encodable = self.__encodables[ti.type_name]
        return Encodable(node.type_identifier, value)


class SchemaDecoder(RawDecoder):

    def encodable_factory(self, node, value):
        """Return the appropriate :class:`.Encodable` instance for the given
        :class:`.Node` `node`.
        """
        meta = get_by_constructor(node.ctr)
        return meta.create(value)
