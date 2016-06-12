# -*- coding: utf-8 -*-
import struct
import sys
import unittest

from amqp.typesystem import const
from amqp.typesystem import decoder
from amqp.utils import compat
from amqp.utils.test import bytes
from amqp.utils.test import DataTypesMixin


class NullDecoderTestCase(unittest.TestCase):

    def test_decode_null(self):
        value = decoder.decode_null(const.NULL, b'')
        self.assertEqual(value, None)


class StringDecoderTestCase(unittest.TestCase, DataTypesMixin):

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


class IntegerDecoderTestCase(unittest.TestCase, DataTypesMixin):

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


class IEEE754BinaryDecoder(unittest.TestCase, DataTypesMixin):

    def test_decode_float(self):
        value = decoder.decode_ieee_754_binary(32, const.FLOAT, self.b_float)
        self.assertEqual(self.p_float, value)

    def test_decode_double(self):
        value = decoder.decode_ieee_754_binary(64, const.DOUBLE, self.b_double)
        self.assertEqual(self.p_double, value)


class BooleanDecoderTestCase(unittest.TestCase, DataTypesMixin):

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


class BinaryDecoderTestCase(unittest.TestCase, DataTypesMixin):

    def test_decode_vbin8(self):
        value = decoder.decode_binary(const.VBIN8, self.b_vbin8)
        self.assertEqual(value, self.b_vbin8)

    def test_decode_vbin32(self):
        value = decoder.decode_binary(const.VBIN32, self.b_vbin32)
        self.assertEqual(value, self.b_vbin32)


class TimestampTestCase(unittest.TestCase, DataTypesMixin):

    def test_decode_unix(self):
        value = decoder.decode_timestamp(const.MS64, self.b_unix)
        self.assertEqual(value, self.p_unix)

    def test_decode_gregorian(self):
        value = decoder.decode_timestamp(const.MS64, self.b_gregorian)
        self.assertEqual(value, self.p_gregorian)

    def test_decode_j2000(self):
        value = decoder.decode_timestamp(const.MS64, self.b_j2000)
        self.assertEqual(value, self.p_j2000)


class UUIDDecoderTestCase(unittest.TestCase, DataTypesMixin):

    def test_decode_uuid4(self):
        value = decoder.decode_uuid(const.UUID, self.b_uuid4)
        self.assertEqual(value, self.p_uuid4)
