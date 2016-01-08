import unittest
import uuid

from amqp.typesystem.utils import get_prep_value


class PreparationTestCase(unittest.TestCase):

    def test_prep_uuid_from_bytes(self):
        u = uuid.uuid4()
        self.assertEqual(get_prep_value('uuid', u.bytes), u)

    def test_prep_uuid_from_int(self):
        u = uuid.uuid4()
        self.assertEqual(get_prep_value('uuid', u.int), u)

    def test_prep_uuid_from_str(self):
        u = uuid.uuid4()
        self.assertEqual(get_prep_value('uuid', u.hex), u)

    def test_prep_uuid_from_uuid(self):
        u = uuid.uuid4()
        self.assertEqual(get_prep_value('uuid', u), u)


if __name__ == '__main__':
    unittest.main()
