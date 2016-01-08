"""Full test of the Composite type feature."""
import copy
import io
import time
import unittest

from amqp.typesystem.basetypes import Composite
from amqp.exc import ValidationError
import amqp


TEST_TYPE = """<?xml version="1.0"?>
<amqp name="one.test" xmlns="http://www.amqp.org/schema/amqp.xsd">
  <section name="CompositeTestCase">
    <type name="CompositeTestCase" class="composite" source="list" provides="frame">
      <descriptor name="one.compositetestcase:list"/>
      <field name="fixed" type="ubyte"/>
      <field name="fixed-timestamp" type="timestamp"/>
      <field name="fixed-mandatory" type="ubyte" mandatory="true"/>
      <field name="fixed-multiple" type="ubyte" multiple="true"/>
      <field name="fixed-multiple-empty" type="ubyte" multiple="true"/>
      <field name="fixed-mandatory-multiple" type="ubyte" mandatory="true" multiple="true"/>
      <field name="variable" type="symbol"/>
      <field name="provider-by-tuple-required" type="*" requires="provider1,provider1" mandatory="true"/>
      <field name="provider-by-tuple" type="*" requires="provider1,provider1"/>
      <field name="provider-by-tuple-multiple" type="*" requires="provider1,provider1" multiple="true"/>
      <field name="provider-by-tuple-multiple-empty" type="*" requires="provider1,provider1" multiple="true"/>
      <field name="provider-by-tuple-multiple-null" type="*" requires="provider1,provider1" multiple="true"/>
    </type>
    <type name="CompositeTestRestricted" class="restricted" source="ubyte" provides="provider1">
        <descriptor name="one.CompositeTestRestricted"/>
        <choice name="foo" value="1"/>
        <choice name="bar" value="2"/>
        <choice name="baz" value="3"/>
    </type>
    <type name="CompositeTestEmptyComposite" class="composite" source="list">
      <descriptor name="one.compositetestcaseemptycomposite:list"/>
      <field name="fixed" type="ubyte"/>
    </type>
  </section>
</amqp>
"""

class CompositeTestCase(unittest.TestCase):
    params = {
        'fixed': 1,
        'fixed_timestamp': int(time.time() * 1000),
        'fixed_mandatory': 2,
        'fixed_multiple': [1,2,3,4,5],
        'fixed_multiple_empty': [],
        'fixed_mandatory_multiple': [6,7,8,9,10],
        'variable': 'foo',
        'provider_by_tuple_required': ('CompositeTestRestricted', 'foo'),
        'provider_by_tuple': ('CompositeTestRestricted', 'bar'),
        'provider_by_tuple_multiple': ('CompositeTestRestricted', ['foo','bar','baz']),
        'provider_by_tuple_multiple_empty': ('CompositeTestRestricted', []),
        'provider_by_tuple_multiple_null': None,
    }
    type_name = 'CompositeTestCase'


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

    def test_create(self):
        fields = self.get_fields()
        obj1 = self.factory(**fields)
        raw = obj1.accept(self.encoder)

        buf = io.BytesIO(raw)
        tree = amqp.parse_buffer(buf)
        obj2 = tree.accept(amqp.RawDecoder(buf)) 
        obj3 = tree.accept(amqp.SchemaDecoder(buf))
        self.assertEqual(obj3.accept(self.encoder), raw)

    def test_is_empty_returns_false(self):
        encodable = self.factory(**self.get_fields())
        self.assertFalse(encodable.is_empty(), repr(encodable.value))

    def test_get(self):
        encodable = self.factory(**self.get_fields())
        self.assertEqual(self.params['fixed'], encodable.get('fixed'))

    def test_set(self):
        encodable = self.factory(**self.get_fields())
        field_name = 'fixed'
        value = 2
        encodable.set(field_name, value)
        self.assertEqual(value, encodable.get(field_name))

    def test_as_dto(self):
        encodable = self.factory(**self.get_fields())
        dto = encodable.as_dto()

    def test_as_dto_with_minimal_fields(self):
        encodable = self.factory(
            fixed_mandatory=2,
            fixed_mandatory_multiple=[1,2,3],
            provider_by_tuple_required=('CompositeTestRestricted','foo')
        )
        dto = encodable.as_dto()

    def test_extra_raises_type_error(self):
        fields = self.get_fields()
        fields['foo'] = amqp.encodable('uint', 1)
        self.assertRaises(TypeError, amqp.encodable, self.type_name, fields)

    def test_missing_mandatory_raises_validation_error(self):
        fields = self.get_fields(exclude=['fixed_mandatory'])
        self.assertRaises(ValidationError, amqp.encodable, self.type_name, fields)

    def test_mixed_array_raises_validation_error(self):
        fields = self.get_fields()
        fields['fixed_multiple'] = [1, 'foo']
        self.assertRaises(ValidationError, amqp.encodable, self.type_name, fields)

    def test_not_satisfied_raises_validation_error(self):
        fields = self.get_fields()
        fields['provider_by_tuple'] = ('uint', 1)
        self.assertRaises(ValidationError, amqp.encodable, self.type_name, fields)

    def test_mixed_array_raises_validation_error_on_polymorphic_field(self):
        fields = self.get_fields()
        fields['provider_by_tuple_multiple'] = ('uint', ['foo', 1])
        self.assertRaises(ValidationError, amqp.encodable, self.type_name, fields)

    def test_invalid_choice_raises(self):
        fields = self.get_fields()
        fields['provider_by_tuple'] = ('CompositeTestRestricted', 1337)
        self.assertRaises(ValidationError, amqp.encodable, self.type_name, fields)

    def test_restricted_is_empty_returns_false(self):
        factory = amqp.create_factory('CompositeTestRestricted')
        encodable = factory('bar')
        self.assertFalse(encodable.is_empty(), encodable.value)

    def test_restricted_init_without_parameters(self):
        factory = amqp.create_factory('CompositeTestRestricted')
        self.assertRaises(ValidationError, factory)
        

if __name__ == '__main__':
    unittest.main()
