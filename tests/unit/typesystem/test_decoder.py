import unittest

from amqp.typesystem.decoder import RawDecoder
import amqp.exc


class RawDecoderTestCase(unittest.TestCase):

    def test_unknown_format_code_raises(self):
        self.assertRaises(amqp.exc.DecodeError,
            RawDecoder.decode, -1, b'')
