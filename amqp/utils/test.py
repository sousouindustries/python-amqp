import struct
import sys


bytes = (lambda value=None: ''.join([struct.pack('!B', x) for x in value])\
    if value is not None else '') if (sys.version_info.major == 2)\
    else bytes

