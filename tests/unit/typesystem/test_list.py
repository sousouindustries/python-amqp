import io
import unittest
import uuid


import amqp
import amqp.typesystem


class ListBaseTestCase(object):
    """Specifies all tests the list encoding must pass."""
    values = None
    type_name = None
    symbolic = 'foo'
    numeric = 1

    def setUp(self):
        self.encoder = amqp.typesystem.Encoder()

    def test_is_empty(self):
        encodable = amqp.encodable_factory(self.type_name, [])
        self.assertTrue(encodable.is_empty())

    def test_encode(self):
        encodable = amqp.encodable_factory(self.type_name, self.values)
        self.encode_parse_tree_decode(encodable)

    def test_encode_with_numeric_descriptor(self):
        encodable = amqp.encodable_factory(
            self.type_name, self.values, nd=self.numeric)
        self.encode_parse_tree_decode(encodable)

    def test_encode_with_symbolic_descriptor(self):
        encodable = amqp.encodable_factory(
            self.type_name, self.values, sd=self.symbolic)
        self.encode_parse_tree_decode(encodable)

    def encode_parse_tree_decode(self, encodable):
        encoded = encodable.accept(self.encoder)
        buf = io.BytesIO(encoded)
        decoder = amqp.typesystem.RawDecoder(buf)
        tree = amqp.typesystem.parse_buffer(buf)
        decoded = tree.accept(decoder)

        self.assertEqual(len(decoded), len(encodable))
        self.assertEqual(decoded.accept(self.encoder), encoded)


class MixedListTestCase(ListBaseTestCase, unittest.TestCase):
    values = [
        amqp.encodable_factory('null', None), # zero
        amqp.encodable_factory('boolean', True), # fixed-one
        amqp.encodable_factory('uint', 0), # fixed-zero
        amqp.encodable_factory('float', 1.0),
        amqp.encodable_factory('double', 1.0),
        amqp.encodable_factory('uuid', uuid.uuid4()), # fixed-sixteen
        amqp.encodable_factory('binary', b'foo'), # variable-one
        amqp.encodable_factory('binary', b'f' * 256), # variable-four
        amqp.encodable_factory('string', 'foo'), # variable-one
        amqp.encodable_factory('string', 'f' * 256), # variable-four
    ]
    type_name = 'list'
