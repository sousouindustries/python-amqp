import datetime
import decimal
import functools
import re
import uuid

from amqp.const import ENDIAN
from amqp.utils import compat
from amqp.typesystem import const
from amqp.typesystem.const import SYM8
from amqp.typesystem.const import SYM32
from amqp.typesystem.const import SMALLULONG
from amqp.typesystem.const import ULONG
from amqp.exc import EncoderDoesNotExist
#from amqp.utils import datetime_to_timestamp


TYPE_LENGTH = {
    0x4: 0,
    0x5: 1,
    0x6: 2,
    0x7: 4,
    0x8: 8,
    0x9: 16,
    0xA: 1,
    0xB: 4,
    0xC: 1,
    0xD: 4,
    0xE: 1,
    0xF: 4
}


def strip_namespace(document):
    """Strip the namespace from an XML document `document`."""
    return re.sub(' xmlns="[^"]+"', '', document, count=1)


def get_type_length(format_code):
    """Return the binary length a fixed-width AMQP data type, the size
    indicator length of a variable width type, or the length of the size and
    count indicators of compound and array types.
    """
    category = format_code >> 4
    if category not in TYPE_LENGTH:
        raise KeyError(category, "Unknown category: " + hex(format_code))
    return TYPE_LENGTH[category]


def is_collection(format_code):
    """Returns ``True`` if `format_code` is a collection (``list``,
    ``map``, ``array``).
    """
    return ((format_code >> 4) >= 0xC) or format_code == 0x45


def is_variable(format_code):
    """Returns ``True`` if `format_code` is of variable length."""
    return (format_code >> 4) >= 0xA


def is_array(format_code):
    """Returns ``True`` if `format_code` is an ``array``."""
    return (format_code >> 4) in (0xE0, 0xF0)


def is_compound(format_code):
    """Returns ``True`` if `format_code` is a ``list``."""
    return (format_code >> 4) in (0xC, 0xD)


#def unpack_descriptor(value):
#    """Unpacks a numeric descriptor from its wire-level format to a string.
#
#    >>> from amqp.lib.codec import stream
#    >>> stream.unpack_descriptor((0x00 << 32) | 0x40)
#    '0x0:0x40'
#    """
#    assert isinstance(value, int), "value must be an integer"
#    domain_id = value >> 32
#    descriptor_id = value & ((1<<(32-1))-1)
#    return "{0}:{1}".format(hex(domain_id), hex(descriptor_id))


def pack_descriptor(value):
    """Packs a hex representation of a numeric descriptor to an unsigned
    long integer.
    """
    domain_id, descriptor_id = map(lambda x: int(x, 16), value.split(':'))
    return (domain_id << 32) | descriptor_id


def prep_timestamp(value):
    if isinstance(value, datetime.date):
        value= datetime_to_timestamp(value)
    elif not isinstance(value, int):
        value = int(value)
    return value


def prep_bytes(value):
    if isinstance(value, str):
        value = value.encode()
    return bytes(value)


def prep_string(encoding, value):
    return compat.force_str(value.encode(encoding), encoding=encoding)


def prep_boolean(value):
    if value == 'true':
        value = True
    elif value == 'false':
        value = False
    else:
        value = bool(value)
    return value


def prep_uuid(value):
    if not isinstance(value, uuid.UUID):
        kwargs = {}
        if isinstance(value, compat.integer_types):
            kwargs['int'] = value
        elif isinstance(value, str) and len(value) == 32:
            kwargs['hex'] = value
        elif isinstance(value, bytes):
            kwargs['bytes'] = value
        else:
            raise NotImplementedError(
                "Cannot cast {0} to UUID.".format(type(value).__name__)
            )
        try:
            value = uuid.UUID(**kwargs)
        except Exception as e:
            raise ValueError(value)
    return value


#: A mapping of Python types to AMQP primitive type names. This is
#: used to coerce objects to the appropriate type.
PYTHON_TYPE_MAP = {
    'null'      : lambda x: None,
    'boolean'   : prep_boolean,
    'byte'      : int,
    'short'     : int,
    'int'       : int,
    'long'      : int,
    'ubyte'     : int,
    'ushort'    : int,
    'uint'      : int,
    'ulong'     : int,
    'float'     : float,
    'double'    : float,
    'decimal32' : decimal.Decimal,
    'decimal64' : decimal.Decimal,
    'decimal128': decimal.Decimal,
    'char'      : functools.partial(prep_string, 'utf-32-be'),
    'timestamp' : prep_timestamp,
    'uuid'      : prep_uuid,
    'binary'    : prep_bytes,
    'string'    : functools.partial(prep_string, 'utf-8'),
    'symbol'    : functools.partial(prep_string, 'ascii'),
    'list'      : lambda x: list(x) if (x is not None) else [],
    'array'     : lambda x: list(x) if (x is not None) else [],
    'map'       : lambda x: dict(x) if (x is not None) else {}
}


def get_prep_value(type_name, value):
    """Cast a Python object to the correct type for encoding to `type_name`.

    Args:
        type_name (:class;`str`): an AMQP primitive type name.
        value: the Python object to coerce.

    Returns:
        the coerced object.
    """
    if value is not None:
        if type_name not in PYTHON_TYPE_MAP:
            raise EncoderDoesNotExist(type_name)
        return PYTHON_TYPE_MAP[type_name](value)



#: A mapping of AMQP format codes to type names.
FORMAT_CODE_MAP = {
    const.NULL      : 'null',
    const.BOOLEAN   : 'boolean',
    const.TRUE      : 'boolean',
    const.FALSE     : 'boolean',
    const.BYTE      : 'byte',
    const.SHORT     : 'short',
    const.INT       : 'int',
    const.SMALLINT  : 'int',
    const.LONG      : 'long',
    const.SMALLLONG : 'long',
    const.UBYTE     : 'ubyte',
    const.USHORT    : 'ushort',
    const.UINT      : 'uint',
    const.UINT0     : 'uint',
    const.SMALLUINT : 'uint',
    const.ULONG     : 'ulong',
    const.ULONG0    : 'ulong',
    const.SMALLULONG: 'ulong',
    const.FLOAT     : 'float',
    const.DOUBLE    : 'double',
    const.DECIMAL32 : 'decimal32',
    const.DECIMAL64 : 'decimal64',
    const.DECIMAL128: 'decimal128',
    const.CHAR      : 'char',
    const.MS64      : 'timestamp',
    const.UUID      : 'uuid',
    const.VBIN8     : 'binary',
    const.VBIN32    : 'binary',
    const.STR8      : 'string',
    const.STR32     : 'string',
    const.SYM8      : 'symbol',
    const.SYM32     : 'symbol',
    const.LIST0     : 'list',
    const.LIST8     : 'list',
    const.LIST32    : 'list',
    const.MAP8      : 'map',
    const.MAP32     : 'map',
    const.ARRAY8    : 'array',
    const.ARRAY32   : 'array',
}


def get_type_name(format_code):
    """Return a string holding the symbolic type name for the given
    `format_code`.
    """
    return FORMAT_CODE_MAP[format_code]

