import unittest

from amqp.typesystem import const
from amqp.typesystem import encoder
from amqp.utils.test import DataTypesMixin


class IntegerEncoderTestCase(unittest.TestCase, DataTypesMixin):

    def test_encode_ubyte(self):
        stream = encoder.encode_ubyte(self.p_ubyte)
        self.assertEqual(stream, self.b_ubyte)

    def test_encode_length_ubyte(self):
        stream = encoder.encode_ubyte(self.p_ubyte)
        self.assertEqual(len(stream), 1)

    def test_encode_ushort(self):
        stream = encoder.encode_ushort(self.p_ushort)
        self.assertEqual(stream, self.b_ushort)

    def test_encode_length_ushort(self):
        stream = encoder.encode_ushort(self.p_ushort)
        self.assertEqual(len(stream), 2)

    def test_encode_uint(self):
        stream = encoder.encode_uint(self.p_uint)
        self.assertEqual(stream, self.b_uint)

    def test_encode_length_uint(self):
        stream = encoder.encode_uint(self.p_uint)
        self.assertEqual(len(stream), 4)

    def test_encode_uint0(self):
        stream = encoder.encode_uint(self.p_uint0)
        self.assertEqual(stream, self.b_uint0)

    def test_encode_length_uint0(self):
        stream = encoder.encode_uint(self.p_uint0)
        self.assertEqual(len(stream), 0)

    def test_encode_smalluint(self):
        stream = encoder.encode_uint(self.p_smalluint)
        self.assertEqual(stream, self.b_smalluint)

    def test_encode_length_smalluint(self):
        stream = encoder.encode_uint(self.p_smalluint)
        self.assertEqual(len(stream), 1)

    def test_encode_ulong(self):
        stream = encoder.encode_ulong(self.p_ulong)
        self.assertEqual(stream, self.b_ulong)

    def test_encode_length_ulong(self):
        stream = encoder.encode_ulong(self.p_ulong)
        self.assertEqual(len(stream), 8)

    def test_encode_ulong0(self):
        stream = encoder.encode_ulong(self.p_ulong0)
        self.assertEqual(stream, self.b_ulong0)

    def test_encode_length_ulong0(self):
        stream = encoder.encode_ulong(self.p_ulong0)
        self.assertEqual(len(stream), 0)

    def test_encode_smallulong(self):
        stream = encoder.encode_ulong(self.p_smallulong)
        self.assertEqual(stream, self.b_smallulong)

    def test_encode_length_smallulong(self):
        stream = encoder.encode_ulong(self.p_smallulong)
        self.assertEqual(len(stream), 1)

    def test_encode_byte(self):
        stream = encoder.encode_byte(self.p_byte)
        self.assertEqual(stream, self.b_byte)

    def test_encode_length_byte(self):
        stream = encoder.encode_byte(self.p_byte)
        self.assertEqual(len(stream), 1)

    def test_encode_short(self):
        stream = encoder.encode_short(self.p_short)
        self.assertEqual(stream, self.b_short)

    def test_encode_length_short(self):
        stream = encoder.encode_short(self.p_short)
        self.assertEqual(len(stream), 2)

    def test_encode_int(self):
        stream = encoder.encode_int(self.p_int)
        self.assertEqual(stream, self.b_int)

    def test_encode_length_int(self):
        stream = encoder.encode_int(self.p_int)
        self.assertEqual(len(stream), 4)

    def test_encode_smallint(self):
        stream = encoder.encode_int(self.p_smallint)
        self.assertEqual(stream, self.b_smallint)

    def test_encode_length_smallint(self):
        stream = encoder.encode_int(self.p_smallint)
        self.assertEqual(len(stream), 1)

    def test_encode_long(self):
        stream = encoder.encode_long(self.p_long)
        self.assertEqual(stream, self.b_long)

    def test_encode_length_long(self):
        stream = encoder.encode_long(self.p_long)
        self.assertEqual(len(stream), 8)

    def test_encode_smalllong(self):
        stream = encoder.encode_long(self.p_smalllong)
        self.assertEqual(stream, self.b_smalllong)

    def test_encode_length_smalllong(self):
        stream = encoder.encode_long(self.p_smalllong)
        self.assertEqual(len(stream), 1)
