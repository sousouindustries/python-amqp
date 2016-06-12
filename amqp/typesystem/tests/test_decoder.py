# -*- coding: utf-8 -*-
import datetime
import struct
import sys
import unittest
import uuid

from amqp.typesystem import const
from amqp.typesystem import decoder
from amqp.utils import compat
from amqp.utils.test import bytes


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


class BinaryDecoderTestCase(unittest.TestCase):
    b_vbin8 = bytes([255,255])
    b_vbin32 = bytes([255,255,255])

    def test_decode_vbin8(self):
        value = decoder.decode_binary(const.VBIN8, self.b_vbin8)
        self.assertEqual(value, self.b_vbin8)

    def test_decode_vbin32(self):
        value = decoder.decode_binary(const.VBIN32, self.b_vbin32)
        self.assertEqual(value, self.b_vbin32)


class TimestampTestCase(unittest.TestCase):
    p_unix = datetime.datetime(1970, 1, 1)
    p_gregorian = datetime.datetime(1, 1, 1)
    p_j2000 = datetime.datetime(2000, 1, 1)
    b_unix = bytes([0,0,0,0,0,0,0,0])
    b_gregorian = bytes([255, 255, 199, 124, 237, 211, 40, 0])
    b_j2000 = bytes([0, 0, 0, 220, 106, 207, 172, 0])

    def test_decode_unix(self):
        value = decoder.decode_timestamp(const.MS64, self.b_unix)
        self.assertEqual(value, self.p_unix)

    def test_decode_gregorian(self):
        value = decoder.decode_timestamp(const.MS64, self.b_gregorian)
        self.assertEqual(value, self.p_gregorian)

    def test_decode_j2000(self):
        value = decoder.decode_timestamp(const.MS64, self.b_j2000)
        self.assertEqual(value, self.p_j2000)


class UUIDDecoderTestCase(unittest.TestCase):
    b_uuid4 = bytes([206, 142, 2, 208, 203, 108, 70,
        106, 184, 223, 216, 52, 241, 121, 49, 68])
    p_uuid4 = uuid.UUID('ce8e02d0-cb6c-466a-b8df-d834f1793144')

    def test_decode_uuid4(self):
        value = decoder.decode_uuid(const.UUID, self.b_uuid4)
        self.assertEqual(value, self.p_uuid4)
