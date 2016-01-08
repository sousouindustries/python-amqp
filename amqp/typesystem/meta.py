from collections import Iterable
from collections import Mapping
from collections import namedtuple
from collections import OrderedDict

from amqp.const import NOT_PROVIDED

from amqp.exc import ValidationError
from amqp.typesystem.basetypes import Array
from amqp.typesystem.basetypes import Composite
from amqp.typesystem.basetypes import Scalar
from amqp.typesystem.basetypes import Restricted
from amqp.typesystem import basetypes
from amqp.typesystem.field import Field
from amqp.typesystem.registry import get_by_type_name
from amqp.typesystem.utils import get_prep_value


class Meta(object):
    """Represents an AMQP type definition."""
    DEFAULT = object()
    type_map = {
        ('primitive', None): basetypes.Scalar,
        ('primitive', 'array'): basetypes.Array,
        ('primitive', 'list'): basetypes.List,
        ('primitive', 'map'): basetypes.Map,
        ('composite', 'list'): basetypes.Composite,
        ('restricted', None): basetypes.Restricted
    }

    @property
    def fields(self):
        return list(self.__fields.values())

    @staticmethod
    def descriptor_from_element(element):
        numeric = element.get('code')
        if numeric is not None:
            domain, ident = numeric.split(':')
            numeric = (int(domain, 16) << 32) | int(ident, 16)
        return {
            'symbolic': element.get('name'),
            'numeric': numeric
        }

    @staticmethod
    def split_comma_separated(value):
        if value is None:
            return []
        parts = map(str.strip, value.split(','))
        return list(filter(bool, parts))

    @classmethod
    def fromelement(cls, registry, element):
        """Construct a new :class:`Meta` instance from an XML element."""
        # These three attributes should always be present on an AMQP type
        # definition.
        encodings = []
        fields = []
        choices = []
        kwargs = {
            'type_name': element.get('name'),
            'type_class': element.get('class'),
            'source': element.get('source'),
            'encodings': encodings,
            'fields': fields,
            'provides': cls.split_comma_separated(
                element.get('provides')
            ),
            'choices': choices
        }
        type_class = kwargs['type_class']

        # Iterate over the elements' children. Some rules apply:
        #
        # 1. Primitive types may only declare encoding elements.
        # 2. Composite types may declare field or descriptor elements.
        # 3. Restricted types may declare choice or descriptor elements.
        for child in element:
            tag = child.tag
            if tag == 'encoding':
                assert type_class == 'primitive', type_class
                encodings.append({
                    'name': child.get('name', cls.DEFAULT),
                    'category': child.get('category'),
                    'code': int(child.get('code'), 16),
                    'width': int(child.get('width'))
                })
            elif tag == 'descriptor':
                assert type_class in ('restricted','composite')
                kwargs.update(cls.descriptor_from_element(child))
            elif tag == 'field':
                assert type_class == 'composite'
                assert not (child.get('type') == '*' and child.get('default'))
                requires = child.get('requires')
                field_params = {
                    'field_name': child.get('name'),
                    'type_name': child.get('type'),
                    'requires': set(cls.split_comma_separated(requires)),
                    'mandatory': child.get('mandatory') == 'true',
                    'multiple': child.get('multiple') == 'true',
                    'raw_default': child.get('default')
                }
                fields.append(Field(**field_params))
            elif tag == 'choice':
                assert type_class == 'restricted'
                choices.append([
                    child.get('name'),
                    get_prep_value(kwargs['source'], child.get('value'))
                ])
            else:
                raise NotImplementedError("Invalid element: " + tag)

        return cls(registry, **kwargs)

    def __init__(self, registry, type_name, type_class, source, provides=None, 
        symbolic=None, numeric=None, fields=None, choices=None, encodings=None):
        """Initialize a new :class:`Meta` instance."""
        self.registry = registry
        self.type_name = type_name
        self.type_class = type_class
        self.source = source
        self.provides = set(provides or [])
        self.symbolic = symbolic
        self.numeric = numeric
        self.__fields = OrderedDict((x.attname, x) for x in (fields or []))
        self.choices = dict(choices or [])
        self.encodings = encodings or []
        self.encodable_class = \
            self.type_map.get((self.type_class, self.source))\
            or self.type_map[(self.type_class, None)]

        # Register the Meta class under its type name, format codes and
        # descriptors.
        self.registry.register_type_name(self.type_name, self)
        for encoding in self.encodings:
            code = encoding.get('code')
            if code is not None:
                self.registry.register_format_code(code, self)

        if self.symbolic:
            self.registry.register_descriptor(self.symbolic, self)

        if self.numeric:
            self.registry.register_descriptor(self.numeric, self)

        # TODO: This is a quick hack to put the index number on the
        # fields to their values can be retrieved from the list on
        # the composite type. We also create the Data Transfer Object
        # class (namedtuple) here.
        names = []
        class_name = self.type_name\
            .replace('-','_')\
            .replace('.','_')
        for i, field in enumerate(self.fields):
            field.index = i
            names.append(field.attname)

        self.dto_class = namedtuple(class_name, names)

    def create(self, value):
        """Create a new instance of the defined AMQP type. Return an
        :class:`.Encodable` instance representing the cleaned and validated
        input.
        """
        value = self.clean(value)

        if self.type_class == 'primitive':
            # If the Meta represents a primitive type, simple clean and validate
            # and return the appropriate Encodable implementation.
            return basetypes.encodable_factory(self.type_name, value)

        elif self.type_class == 'restricted':
            source =  get_by_type_name(self.source)
            return Restricted.frommeta(self, source.create(value))
        else:
            assert self.type_class == 'composite'
            return Composite.frommeta(self, value)

    def get_field_names(self):
        """Return a list holding the attribute names of the declared fields on
        a composite type.
        """
        return [x.attname for x in self.fields]

    def get_field(self, field_name):
        """Get a composite type field by its name."""
        return self.__fields[field_name]

    def convert_choice(self, raw_value):
        """Converts a value to the choices specified on a restricted
        AMQP type.
        """
        assert isinstance(raw_value, (str, bytes))\
            or not isinstance(raw_value, (Iterable, Mapping)), raw_value
        if not self.choices or raw_value in (set(self.choices.values())):
            return raw_value
        if raw_value not in self.choices:
            raise ValidationError('invalid', self, raw_value, self.choices)
        return self.choices.get(raw_value)

    def create_descriptor(self):
        """Create a :class:`.Scalar` instance representing the descriptor
        of a described type.
        """
        if any([self.symbolic, self.numeric]):
            return Scalar.create('symbol', self.symbolic)\
                if self.symbolic\
                else Scalar.create('uint', self.numeric) 

    def clean(self, value):
        """Cleans a Python object prior to creating an :class:`.Encodable`."""
        if self.choices:
            value = self.convert_choice(value)
        return value

    def is_restricted(self):
        """Return ``True`` if the :class:`Meta` instance represents a
        restricted AMQP type.
        """
        return self.type_class == 'restricted'

    def get_source(self):
        """Return the primitive AMQP type name."""
        return self.source or self.type_name

    def __repr__(self):
        return "<Meta: {0}>".format(self.type_name)
