import io
import unittest

import amqp


class StreamTestCase(unittest.TestCase):

    def test_parse_buffer_raises_eof_on_empty(self):
        buf = io.BytesIO()
        self.assertRaises(EOFError, amqp.parse_buffer, buf)

    def test_parse_buffer_raises_valueerror_on_unknown_format_code(self):
        buf = io.BytesIO(b'\x00\xAA')
        self.assertRaises(ValueError, amqp.parse_buffer, buf)


if __name__ == '__main__':
    unittest.main()
