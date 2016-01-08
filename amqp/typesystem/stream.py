import io

from amqp.typesystem.datastructures import Constructor
from amqp.typesystem.const import ULONG
from amqp.typesystem.const import SMALLULONG
from amqp.typesystem.const import SYM8
from amqp.typesystem.const import SYM32
from amqp.typesystem.utils import get_type_length
from amqp.typesystem.utils import is_array
from amqp.typesystem.utils import is_collection
from amqp.typesystem.utils import is_compound
from amqp.typesystem.utils import is_variable
from amqp.utils import compat


ENDIAN = 'big'


def read_stream(format_code, read):
    """Read an AMQP-encoded value from a stream."""
    return read_fixed(format_code, read)\
        if not is_variable(format_code)\
        else read_variable(format_code, read)


def read_fixed(format_code, read):
    """Read a fixed-length value from an AMQP-encoded datastream.

    Args:
        read: a callable that accepts an integer as its argument, indicating
            the number of octets to be read from the stream, and returns
            a :class:`bytes` object of equal length to the input value.
        format_code (:class:`int`): an AMQP primitive type format
            code.

    Returns:
        bytes
    """
    return read(get_type_length(format_code))


def read_variable(format_code, read):
    """Read a variable-length value from an AMQP-encoded datastream.

    Args:
        read: a callable that accepts an integer as its argument, indicating
            the number of octets to be read from the stream, and returns
            a :class:`bytes` object of equal length to the input value.
        format_code (:class:`int`): an AMQP primitive type format
            code.

    Returns:
        bytes
    """
    n = compat.from_bytes(read(get_type_length(format_code)), ENDIAN)
    return read(n)


def decode_constructor(read):
    """Decodes the constructor of an AMQP-encoded value at the beginning
    of the datastream in file-like object `buf`. Return a tuple indicating
    the format code, width, length, symbolic and numeric decriptor.

    Args:
        read: a callable that accepts an integer as its argument, indicating
            the number of octets to be read from the stream, and returns
            a :class:`bytes` object of equal length to the input value.

    Returns:
        Constructor

    Raises:
        EOFError: may be raised by invoking `read()`.
    """
    symbolic = None
    numeric = None
    raw_format_code = read(1)
    if not raw_format_code:
        raise EOFError("End of AMQP-encoded datastream")

    # The first octet indicates the format code type; 0 for described
    # format codes, non-zero for codec.
    format_code = compat.from_bytes(raw_format_code, ENDIAN)
    if format_code == 0x00:
        # If the value has a described format code, its descriptor is
        # either an unsigned long integer, or a symbol.
        format_code = compat.from_bytes(read(1), ENDIAN)
        if format_code in (ULONG, SMALLULONG):
            numeric =\
                compat.from_bytes(read_stream(format_code, read), ENDIAN)
        elif format_code in (SYM8, SYM32):
            #: Symbol is encoded as ASCII (OASIS 2012: 25).
            symbolic = read_stream(format_code, read)\
                .decode('ascii')
        else:
            raise ValueError(
                "Invalid format code for descriptor: " + str(format_code)
            )

        # Right after the descriptor comes the actual primitive type
        # of the encoded value.
        format_code = compat.from_bytes(read(1), ENDIAN)

    return Constructor(format_code, symbolic, numeric)
