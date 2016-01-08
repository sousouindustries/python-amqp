import unittest

from amqp.typesystem.basetypes import Null


class NullTestCase(unittest.TestCase):

    def test_as_dto_is_none(self):
        obj = Null()
        self.assertTrue(obj.as_dto() is None)
