import copy
import unittest

import amqp


TEST_TYPE = """<?xml version="1.0"?>
<amqp name="one.test" xmlns="http://www.amqp.org/schema/amqp.xsd">
  <section name="DataTransferObjectTestCase">
    <type name="DataTransferObjectTestCase" class="composite" source="list">
      <descriptor name="one.test:list"/>
      <field name="fixed" type="ubyte"/>
    </type>
    <type name="NestedDTO" class="composite" source="list">
      <descriptor name="one.nestedto:list"/>
      <field name="nested" type="DataTransferObjectTestCase"/>
    </type>
  </section>
</amqp>
"""

class DataTransferObjectTestCase(unittest.TestCase):
    params = {
        'fixed': 1,
    }
    type_name = 'DataTransferObjectTestCase'

    def get_fields(self, exclude=None):
        exclude = exclude or []
        fields = copy.deepcopy(self.params)
        [fields.pop(x, None) for x in exclude]
        return fields

    @classmethod
    def setUpClass(cls):
        amqp.loader.load_xml(TEST_TYPE)
        cls.encoder = amqp.SchemaEncoder()
        cls.factory = amqp.create_factory(
            cls.type_name,
            validators=[lambda x: x]
        )

    def test_factory(self):
        factory = amqp.DTO.factory('DataTransferObjectTestCase')

    def test_factory_invoke(self):
        factory = amqp.DTO.factory('DataTransferObjectTestCase')
        encodable = factory(fixed=1).as_encodable()
        self.assertEqual(encodable.get('fixed'), 1, encodable)

    def test_nested_dto(self):
        factory = amqp.DTO.factory('NestedDTO')
        encodable = factory(
            nested=amqp.DTO.factory('DataTransferObjectTestCase')(fixed=1)
        ).as_encodable()
