import unittest

import amqp


class MapTestCase(unittest.TestCase):
    type_name = 'map'

    def test_is_empty_is_true_for_empty(self):
        encodable = amqp.encodable_factory(self.type_name, {})
        self.assertTrue(encodable.is_empty())
