import unittest

from amqp.typesystem.basetypes import Scalar


class ScalarTestCase(unittest.TestCase):
    type_name = 'uint'
    value = 1

    def test_as_dto_returns_value(self):
        obj = Scalar.create(self.type_name, self.value)
        self.assertEqual(obj.as_dto(), self.value)
