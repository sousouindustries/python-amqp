import io
import unittest


import amqp
import amqp.typesystem


class ArrayBaseTestCase(object):
    """Specifies all tests the array encoding must pass."""
    values = None
    type_name = None
    symbolic = 'foo'
    numeric = 1

    def setUp(self):
        self.encoder = amqp.typesystem.Encoder()

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

    def test_as_dto_returns_input(self):
        encodable = amqp.encodable_factory(self.type_name, self.values)
        self.assertEqual(encodable.as_dto(), self.values)


class FixedArrayTestCase(ArrayBaseTestCase, unittest.TestCase):
    values = [1, 2, 3]
    type_name = 'uint'


class EmptyFixedArrayTestCase(ArrayBaseTestCase, unittest.TestCase):
    values = []
    type_name = 'uint'


class VariableArrayTestCase(ArrayBaseTestCase, unittest.TestCase):
    values = ['foo','bar','baz']
    type_name = 'string'


class EmptyVariableArrayTestCase(ArrayBaseTestCase, unittest.TestCase):
    values = []
    type_name = 'string'


class MixedArrayTestCase(unittest.TestCase):

    def test_append_raises_typeerror(self):
        array = amqp.encodable_factory('array', [])
        member1 = amqp.encodable_factory('uint', 1)
        member2 = amqp.encodable_factory('symbol', 'foo')
        array.append(member1)
        self.assertRaises(TypeError, array.append, member2)


@unittest.skip
class ArrayArrayTestCase(ArrayBaseTestCase, unittest.TestCase):
    values = [
        amqp.encodable_factory('string', ['foo','bar','baz']),
        amqp.encodable_factory('uint', [1, 2, 3])
    ]
    type_name = 'array'


if __name__ == '__main__':
    unittest.main()
