import unittest

from amqp.typesystem import const
from amqp.typesystem import decoder


class NullDecoderTestCase(unittest.TestCase):

    def test_decode_null(self):
        value = decoder.decode_null(const.NULL, b'')
        self.assertEqual(value, None)
