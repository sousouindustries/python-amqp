import functools
import struct

from amqp.typesystem import const
from amqp.utils import compat


def encode_int(signed, length, small, zero, value):
    """Encode an integer to bytes.

    Args:
        signed: ``True`` if the integer should be represented signed.
        length: the default encoding length.
        small: ``True`` if the integer is allowed to be encoded as
            a single-octet value .e.g. `value` < 128/256.
        zero: ``True`` if the integer type support zero length encoding
            of ``0``.

    Returns:
        bytes
    """
    if zero and value == 0:
        return b''

    if ((signed and value < 128) or (not signed and value < 256))\
    and small:
        length = 1
    return compat.to_bytes(value, length, 'big', signed=signed)


def encode_boolean(value):
    return compat.to_bytes(int(bool(value)), 1, 'big')


def encode_ieee754_binary(template, value):
    return struct.pack('!' + template, value)


def encode_uuid(value):
    return value.bytes


def encode_binary(value):
    return value


def encode_string(encoding, value):
    return value.encode(encoding)


def encode_constructor(default, short, zero, length, n=None, descriptor=None):
    """Encode a constructor based on the length of a value.

    Args:
        default: the default format code for the data type.
        short: an integer representing the short (1 octet) format
            code, if applicable.
        zero: an integer representing the zero-length format code,
            if applicable.
        length: an integer representing the binary length of the encoded
            value.
        n: an integer specifying the member count, for ``array``, ``map``
            and ``list`` types.
        descriptor: the AMQP-encoded representation of the type descriptor,
            may be None.
    """
    count = n or length
    format_code = default
    if length == 0 and zero:
        format_code = zero
    elif max(length + 1, count) < 256 and short:
        format_code = short

    subcategory = format_code >> 4
    format_code = compat.to_bytes(format_code, 1, 'big')
    return (
        subcategory,
        format_code if (descriptor is None)\
        else b'\x00' + descriptor + format_code
    )


class Encoder(object):
    __encoders = {
        'null'      : lambda *a, **k: b'\x40',
        'boolean'   : encode_boolean,
        'byte'      : functools.partial(encode_int, True, 1, False, False),
        'short'     : functools.partial(encode_int, True, 2, False, False),
        'int'       : functools.partial(encode_int, True, 4, True, True),
        'long'      : functools.partial(encode_int, True, 8, True, True),
        'ubyte'     : functools.partial(encode_int, False, 1, False, False),
        'ushort'    : functools.partial(encode_int, False, 2, False, False),
        'uint'      : functools.partial(encode_int, False, 4, True, True),
        'ulong'     : functools.partial(encode_int, False, 8, True, True),
        'timestamp' : functools.partial(encode_int, False, 8, True, True),
        'float'     : functools.partial(encode_ieee754_binary, 'f'),
        'double'    : functools.partial(encode_ieee754_binary, 'd'),
        'uuid'      : encode_uuid,
        'binary'    : encode_binary,
        'string'    : functools.partial(encode_string, "utf-8"),
        'symbol'    : functools.partial(encode_string, "ascii"),
    }
    __constructors = {
        'null'      : lambda *a, **k: (0x40 >> 4, b''),
        'boolean'   : functools.partial(encode_constructor, const.BOOLEAN, None, None),
        'byte'      : functools.partial(encode_constructor, const.BYTE, None, None),
        'short'     : functools.partial(encode_constructor, const.SHORT, None, None),
        'int'       : functools.partial(encode_constructor, const.INT, const.SMALLINT, None),
        'long'      : functools.partial(encode_constructor, const.LONG, const.SMALLLONG, None),
        'ubyte'     : functools.partial(encode_constructor, const.UBYTE, None, None),
        'ushort'    : functools.partial(encode_constructor, const.USHORT, None, None),
        'uint'      : functools.partial(encode_constructor, const.UINT, const.SMALLUINT, const.UINT0),
        'ulong'     : functools.partial(encode_constructor, const.ULONG, const.SMALLULONG, const.ULONG0),
        'timestamp' : functools.partial(encode_constructor, const.MS64, None, None),
        'float'     : functools.partial(encode_constructor, const.FLOAT, None, None),
        'double'    : functools.partial(encode_constructor, const.DOUBLE, None, None),
        'uuid'      : functools.partial(encode_constructor, const.UUID, None, None),
        'binary'    : functools.partial(encode_constructor, const.VBIN32, const.VBIN8, None),
        'string'    : functools.partial(encode_constructor, const.STR32, const.STR8, None),
        'symbol'    : functools.partial(encode_constructor, const.SYM32, const.SYM8, None),
        'list'      : functools.partial(encode_constructor, const.LIST32, const.LIST8, const.LIST0),
        'array'     : functools.partial(encode_constructor, const.ARRAY32, const.ARRAY8, None),
    }

    def encode(self, encodable, with_constructor):
        """Encodes an encodable object.

        Args:
            encodable: an :class:`.Encodable` instance.
            with_constructor: ``True`` if the constructor should be
                prepended to the value.

        Returns
            bytes
        """
        constructor = b''
        value = self.get_encoder(encodable)(encodable.value)
        if with_constructor:
            sub, constructor = self.encode_constructor(encodable, value)

            # Prepend the length for variable length types, and the length
            # and count for collection types.
            if sub <= 0x9: # Empty or not variable, nothing to do
                pass
            elif sub == 0xA: # variable-one
                constructor += compat.to_bytes(len(value), 1, 'big')
            elif sub == 0xB: # variable-four
                constructor += compat.to_bytes(len(value), 4, 'big')
            else:
                raise NotImplementedError(hex(sub), value, encodable)
        return constructor + value

    def encode_constructor(self, encodable, value, count=None):
        """Encode the constructor for the given `value`.

        Args:
            encodable: an :class:`.Encodable` instance.
            value: a byte-sequence representing the AMQP-encoded presentation
                of `encodable`.
            count: the number of members, if applicable.

        Returns:
            bytes
        """
        size = len(value)
        descriptor = None
        if encodable.descriptor:
            descriptor = encodable.descriptor.accept(self)
        return self._encode_constructor(
            encodable.get_source(), size, count, descriptor
        )

    def _encode_constructor(self, type_name, size, count, descriptor):
        return self.__constructors[type_name]\
            (size, count, descriptor)

    def get_encoder(self, encodable):
        """Return the appropriate encoder for the given `encodable`."""
        return self.__encoders[encodable.get_source()]

    def visit(self, encodable):
        """Visits a :class:`.Encodable`."""
        return self.visit_scalar(encodable)\
            if encodable.is_scalar()\
            else self.visit_collection(encodable)

    def visit_scalar(self, encodable):
        return self.encode(encodable, not encodable.is_array_member())

    def visit_collection(self, encodable):
        """Encode all members of the collection and calculate the length and
        count. For ``array`` instances, back-calculate the format codes for
        its members.
        """
        if encodable.is_list() and len(encodable) > 0:
            # For composite instances, NULL members after the mandatory fields
            # may be omitted. At this point, the composite is considered
            # validated so the trailing NULL members can be safely removed.

            while encodable[-1].is_empty():
                encodable.pop()
            pass

        # If the encodable is an array and it has no members, retur NULL. This
        # is a quick fix to prevent undecodable byte-sequences. Since the logic
        # below determines the member constructor based on the largest member,
        # empty arrays have no way of deciding what kind of format code they
        # should embed in their bode. So for the time being we return NULL instead,
        # since making the member type identifier mandatory on constructing Array
        # instances would break a lot of things.
        if encodable.is_array() and len(encodable) == 0:
            return b'\x40'

        members = [x.accept(self) for x in encodable]
        count = len(members)
        body = b''
        if encodable.is_array() and count > 0:
            # For array types, calculate the constructor based on the length
            # of the largest member.
            largest = max(members)
            ref_member = encodable[members.index(largest)]
            sub, ref_ctr = self.encode_constructor(
                ref_member, largest
            )

            # For variable types, encode the length for each member.
            if sub in (0xA, 0xB):
                body = b''.join([self._encode_length(sub, x) for x in members])
            else:
                body = b''.join(members)
            body = ref_ctr + body

        else:
            body = b''.join(members)

        # The size is the length of the body, plus one octed for the format
        # code. If the size exceeds 255, an unsigned integer (4 octets) is
        # used to indicate the size and count.
        size = len(body) + 1
        width = 1
        if size > 255:
            size += 3
            width = 4

        # Get the subcategory and the constructor for the collection. The size and
        # count are now known. The width of the length and count indicators is
        # determined by the size.
        body = compat.to_bytes(size, width, 'big')\
            + compat.to_bytes(count, width, 'big')\
            + body

        # Finally, encode the constructor. The format code is automatically
        # chosen based on the length of the body.
        sub, ctr = self.encode_constructor(encodable, body)

        return ctr + body

    def _encode_length(self, sub, value):
        # Encode the length for variable-one and variable-four
        width = 1 if (sub == 0xA) else 4
        return compat.to_bytes(len(value), width, 'big') + value



class SchemaEncoder(Encoder):
    pass
