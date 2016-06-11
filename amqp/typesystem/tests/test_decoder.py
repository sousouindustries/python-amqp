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
