"""Declares all constants used by the AMQP 1.0 type codec."""
ENDIAN      = 'big'

# The format codes for all AMQP primitive types.
ARRAY8      = 0xe0
ARRAY32     = 0xf0
BYTE        = 0x51
CHAR        = 0x73
DECIMAL32   = 0x74
DECIMAL64   = 0x84
DECIMAL128  = 0x94
DOUBLE      = 0x82
DESCRIBED   = 0x00
FALSE       = 0x42
FLOAT       = 0x72
INT         = 0x71
LIST0       = 0x45
LIST8       = 0xc0
LIST32      = 0xd0
LONG        = 0x81
MAP8        = 0xc1
MAP32       = 0xd1
MS64        = 0x83
NULL        = 0x40
BOOLEAN     = 0x56
TRUE        = 0x41
SHORT       = 0x61
SMALLINT    = 0x54
SMALLLONG   = 0x55
SMALLUINT   = 0x52
SMALLULONG  = 0x53
STR8        = 0xa1
STR32       = 0xb1
SYM8        = 0xa3
SYM32       = 0xb3
UBYTE       = 0x50
UINT        = 0x70
UINT0       = 0x43
ULONG       = 0x80
ULONG0      = 0x44
USHORT      = 0x60
UUID        = 0x98
VBIN8       = 0xa0
VBIN32      = 0xb0


# Subcategories (can be derived from format codes).
FIXED0  = 0x4
FIXED1  = 0x5
FIXED2  = 0x6
FIXED4  = 0x7
FIXED8  = 0x8
FIXED16 = 0x9
VAR1    = 0xA
VAR4    = 0xB
LIST1   = 0xC
LIST4   = 0xD
ARRAY1  = 0xE
ARRAY4  = 0xF
