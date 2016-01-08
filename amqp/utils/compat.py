import struct
import sys


PY3 = sys.version_info.major == 3
PY2 = sys.version_info.major == 2



# The int object in Python 2 does not expose the `to_bytes` method.
if PY3:
    to_bytes = int.to_bytes
    from_bytes = int.from_bytes
    integer_types = (int,)
    force_str = str
    unicode = str


elif PY2:
    int_format_codes = {
        (1, True): 'b',
        (2, True): 'h',
        (4, True): 'i',
        (8, True): 'q',
        (1, False): 'B',
        (2, False): 'H',
        (4, False): 'I',
        (8, False): 'Q',
    }

    def to_bytes(value, length, endian, signed=False):
        format_code = '!' + int_format_codes[(length, signed)]
        return struct.pack(format_code, value)


    def from_bytes(raw, endian, signed=False):
        # In Python3, invoking from_bytes() with an empty byte-sequence
        # returns 0.
        if not raw:
            return 0

        format_code = '!' + int_format_codes[(len(raw), signed)]
        return struct.unpack(format_code, raw)[0]


    integer_types = (int, long)

    def force_str(value, encoding):
        return unicode(value, encoding)
