# -*- coding: utf-8 -*-
import unittest
import sys

from amqp.typesystem import const
from amqp.typesystem import decoder
from amqp.utils import compat


if sys.version_info.major == 2:
    bytes = bytearray


class NullDecoderTestCase(unittest.TestCase):

    def test_decode_null(self):
        value = decoder.decode_null(const.NULL, b'')
        self.assertEqual(value, None)


class StringDecoderTestCase(unittest.TestCase):
    b_sym8 = bytes([102, 111, 111]) # foo
    b_sym32 = bytes(102 for x in range(256))
    b_str8 = bytes([195, 171])
    b_str32 = bytes([195, 171] * 256)

    def test_decode_sym8(self):
        value = decoder.decode_string('ascii', const.SYM8, self.b_sym8)
        self.assertEqual(value, 'foo')

    def test_decode_sym32(self):
        value = decoder.decode_string('ascii', const.SYM8, self.b_sym32)
        self.assertEqual(value, 'f' * 256)

    def test_decode_str8(self):
        value = decoder.decode_string('utf-8', const.SYM8, self.b_str8)
        self.assertEqual(value, u'ë')

    def test_decode_str32(self):
        value = decoder.decode_string('utf-8', const.SYM8, self.b_str32)
        self.assertEqual(value, u'ë' * 256)


class IntegerDecoderTestCase(unittest.TestCase):
    b_ubyte = bytes([1])                # 1
    b_ushort = bytes([1,0])             # 256
    b_uint = bytes([1,0,0,0])           # 16777216
    b_uint0 = bytes()                   # Should be decoded to 0, as an unsigned integer
    b_smalluint = bytes([1])            # 1, decoded to an unsigned integer
    b_ulong = bytes([1,0,0,0,0,0,0,0])  # 72057594037927936
    b_ulong0 = bytes()                  # Should be decoded to 0, as an unsigned long integer
    b_smallulong = bytes([1])           # 1, decoded to an unsigned long integer
    b_byte = bytes([255])               # -1
    b_short = bytes([255,0])            # -256
    b_int = bytes([255,0,0,0])          # -1677216
    b_smallint = bytes([255])           # -1
    b_long = bytes([255,0,0,0,0,0,0,0]) # -72057594037927936
    b_smalllong = bytes([255])          # -1

    def test_decode_ubyte(self):
        value = decoder.decode_integer(False, const.UBYTE, self.b_ubyte)
        self.assertEqual(value, 1)

    def test_decode_ushort(self):
        value = decoder.decode_integer(False, const.USHORT, self.b_ushort)
        self.assertEqual(value, 256)

    def test_decode_uint(self):
        value = decoder.decode_integer(False, const.UINT, self.b_uint)
        self.assertEqual(value, 16777216)

    def test_decode_uint0(self):
        value = decoder.decode_integer(False, const.UINT0, self.b_uint0)
        self.assertEqual(value, 0)

    def test_decode_smalluint(self):
        value = decoder.decode_integer(False, const.SMALLUINT, self.b_smalluint)
        self.assertEqual(value, 1)

    def test_decode_ulong(self):
        value = decoder.decode_integer(False, const.ULONG, self.b_ulong)
        self.assertEqual(value, 72057594037927936)

    def test_decode_ulong0(self):
        value = decoder.decode_integer(False, const.ULONG0, self.b_ulong0)
        self.assertEqual(value, 0)

    def test_decode_smallulong(self):
        value = decoder.decode_integer(False, const.SMALLULONG, self.b_smallulong)
        self.assertEqual(value, 1)

    def test_decode_byte(self):
        value = decoder.decode_integer(True, const.BYTE, self.b_byte)
        self.assertEqual(value, -1)

    def test_decode_short(self):
        value = decoder.decode_integer(True, const.SHORT, self.b_short)
        self.assertEqual(value, -256)

    def test_decode_int(self):
        value = decoder.decode_integer(True, const.INT, self.b_int)
        self.assertEqual(value, -16777216)

    def test_decode_smallint(self):
        value = decoder.decode_integer(True, const.SMALLINT, self.b_smallint)
        self.assertEqual(value, -1)

    def test_decode_long(self):
        value = decoder.decode_integer(True, const.LONG, self.b_long)
        self.assertEqual(value, -72057594037927936)

    def test_decode_smalllong(self):
        value = decoder.decode_integer(True, const.SMALLLONG, self.b_smalllong)
        self.assertEqual(value, -1)


class IEEE754BinaryDecoder(unittest.TestCase):
    b_float = bytes([63, 128, 0, 0])
    b_double = bytes([63, 240, 0, 0, 0, 0, 0, 0])
    p_float = 1.0
    p_double = 1.0

    def test_decode_float(self):
        value = decoder.decode_ieee_754_binary(32, const.FLOAT, self.b_float)
        self.assertEqual(self.p_float, value)

    def test_decode_double(self):
        value = decoder.decode_ieee_754_binary(64, const.DOUBLE, self.b_double)
        self.assertEqual(self.p_double, value)


class BooleanDecoderTestCase(unittest.TestCase):

    def test_decode_true(self):
        value = decoder.decode_boolean(const.TRUE, bytes())
        self.assertEqual(value, True)

    def test_decode_false(self):
        value = decoder.decode_boolean(const.FALSE, bytes())
        self.assertEqual(value, False)

    def test_decode_boolean_true(self):
        value = decoder.decode_boolean(const.BOOLEAN, bytes([1]))
        self.assertEqual(value, True)

    def test_decode_boolean_false(self):
        value = decoder.decode_boolean(const.BOOLEAN, bytes([0]))
        self.assertEqual(value, False)
