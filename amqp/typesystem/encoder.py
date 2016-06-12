import functools

from amqp.typesystem import const
from amqp.utils import compat


def encode_integer(signed, length, small, zero, value):
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

    if ((signed and (128 > value >= -128)) or (not signed and value < 256))\
    and small:
        length = 1
    return compat.to_bytes(value, length, 'big', signed=signed)


encode_ubyte = functools.partial(encode_integer, False, 1, False, False)
encode_ushort = functools.partial(encode_integer, False, 2, False, False)
encode_uint = functools.partial(encode_integer, False, 4, True, True)
encode_ulong = functools.partial(encode_integer, False, 8, True, True)
encode_byte = functools.partial(encode_integer, True, 1, False, False)
encode_short = functools.partial(encode_integer, True, 2, False, False)
encode_int = functools.partial(encode_integer, True, 4, True, False)
encode_long = functools.partial(encode_integer, True, 8, True, False)
