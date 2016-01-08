from collections import Iterable
from collections import Mapping
import collections

from amqp.const import NOT_PROVIDED
from amqp.typesystem.datastructures import TypeIdentifier
from amqp.typesystem.provider import Provider


class Encodable(object):

    @property
    def value(self):
        return self.__value

    def __init__(self, value):
        self.__value = value
        self.__in_array = False

    def accept(self, encoder):
        """Accepts a visitor."""
        return encoder.visit(self)

    def get_source(self):
        """Return a string representing the source (primitive) AMQP type
        of the :class:`Encodable`.
        """
        return self.type_name

    def is_scalar(self):
        """Return ``True`` if the :class:`Encodable` is a scalar value."""
        return self.get_source() not in ('array','map','list')

    def is_array(self):
        """Return ``True`` if the :class:`AMQPType` is an ``array``."""
        return self.get_source() == 'array'

    def is_list(self):
        """Return ``True`` if the :class:`AMQPType` is a ``list``."""
        return self.get_source() == 'list'

    def add_to_array(self, array):
        """Add the :class:`.Encodable` to an ``array``."""
        self.__in_array = True
        array.append(self)

    def is_array_member(self):
        """Return ``True`` if the object is a member of an ``array``."""
        return self.__in_array

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        raise NotImplementedError


class AMQPType(Encodable):

    @property
    def type_name(self):
        return self.type_identifier.type_name

    @property
    def descriptor(self):
        """Return a :class:`Scalar` instance representing the descriptor."""
        type_name, sd, nd, _ = self.type_identifier
        if nd: # Prefer numeric over symbolic
            descriptor = Scalar.create('ulong', nd)
        elif sd:
            descriptor = Scalar.create('symbol', sd)
        else:
            descriptor = None
        return descriptor

    @classmethod
    def create(cls, type_name, value, nd=None, sd=None, in_array=False, **kwargs):
        """Create a new :class:`AMQPType` instance."""
        identifier = TypeIdentifier(type_name, sd, nd, None)
        return cls(identifier, value, **kwargs)

    def __init__(self, type_identifier, value, **kwargs):
        assert isinstance(type_identifier, TypeIdentifier), value
        self.type_identifier = type_identifier
        Encodable.__init__(self, value)


class Null(AMQPType):
    # A special type representing the NULL value.

    def __init__(self, *args, **kwargs):
        AMQPType.__init__(self, TypeIdentifier('null', None, None, None), None)

    def as_dto(self):
        """Project the :class:`Encodable` as a Data Transfer Object (DTO)."""
        return None

    def get_source(self):
        return 'null'

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        return True

    def __len__(self):
        return 0

    def __repr__(self):
        return "<NULL>"


class Scalar(AMQPType):

    def __init__(self, *args, **kwargs):
        super(Scalar, self).__init__(*args, **kwargs)

    def as_dto(self):
        """Project the :class:`Encodable` as a Data Transfer Object (DTO)."""
        return self.value

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        return self.get_source() == 'null'

    def __repr__(self):
        return "<Scalar ({0}): {1}>"\
            .format(self.type_identifier.type_name, repr(self.value))


class Array(AMQPType):

    def __init__(self, type_identifier, members, **kwargs):
        super(Array, self).__init__(type_identifier, [])
        self.__member_type = None
        for member in members:
            member.add_to_array(self)

    def as_dto(self):
        """Project the :class:`Encodable` as a Data Transfer Object (DTO)."""
        return [x.as_dto() for x in self.value]

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        return len(self) == 0

    def append(self, value):
        """Append a value to the array."""
        source = value.get_source()
        if self.__member_type is None:
            self.__member_type = source
        elif self.__member_type != source:
            raise TypeError("Array instances must be monomorphic collections.")
        self.value.append(value)

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<Array: {0}>".format(repr(self.value))


class List(AMQPType):

    def __init__(self, type_identifier, members, *args, **kwargs):
        super(List, self).__init__(type_identifier, members, **kwargs)

    def pop(self, *args):
        return self.value.pop(*args)

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        return len(self) == 0

    def __getitem__(self, key):
        return self.value[key]

    def __len__(self):
        return len(self.value)

    def __repr__(self):
        return "<List: {0}>".format(repr(self.value))


class Map(AMQPType):

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        return len(self) == 0

    def __len__(self):
        return len(self.value)


class Composite(List, Provider):

    @classmethod
    def frommeta(cls, meta, fields):
        """Create a new :class:`Composite` using a :class:`.Meta`
        instance.
        """
        instance = cls.create(meta.type_name, [],
            nd=meta.numeric,
            sd=meta.symbolic,
            meta=meta
        )

        # Iterate over the fields defined in the Meta instance to
        # get the field values in the right order.
        for i, attname in enumerate(meta.get_field_names()):
            if isinstance(fields, list): # During decoding.
                try:
                    value = fields.pop(0)
                except IndexError:
                    value = NOT_PROVIDED
            else:
                value = fields.pop(attname, NOT_PROVIDED)
            instance.append(value)

        # If there are fields remaining, this is considered a typeerror.
        if fields:
            raise TypeError(
                "Fields remaining: {0}".format(list(fields))
            )

        return instance

    def __init__(self, *args, **kwargs):
        self.meta = kwargs.pop('meta', None)
        assert self.meta is not None
        Provider.__init__(self, self.meta.provides)
        List.__init__(self, *args, **kwargs)

    def as_dto(self):
        """Project the :class:`Composite` as a Data Transfer Object
        (DTO).
        """
        values = []
        for field in self.meta.fields:
            values.append(
                self.value[field.index].as_dto())
        return self.meta.dto_class(*values)

    def get(self, field_name, encodable=False):
        """Return the Python representation of the field identified
        by `field_name`.
        """
        field = self.meta.get_field(field_name)
        return self.value[field.index].value\
            if not encodable\
            else self.value[field.index]

    def set(self, field_name, value):
        """Set field `field_name` of the composite type to `value`."""
        field = self.meta.get_field(field_name)
        self.value[field.index] = field.clean(value)

    def get_source(self):
        """Return a string representing the source (primitive) AMQP type
        of the :class:`Encodable`.
        """
        return 'list'

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        # Composite types are never empty; missing values are
        # provided as Null objects.
        return False

    def append(self, value):
        """Appends a value to the Composite type instance. The clean()
        method of the declared fields is invoked if the input value is
        not a :class:`.Encodable` instance.
        """
        if not isinstance(value, Encodable):
            field = self.meta.fields[len(self.value)]
            value = field.clean(value)
        self.value.append(value)

    def __repr__(self):
        return "<Composite: {0}>".format(repr(self.value))


class RestrictedArray(Array, Provider):

    @classmethod
    def frommeta(cls, meta, members):
        return cls.create('array', members, meta=meta)

    def __init__(self, type_identifier, members, **kwargs):
        self.__meta = kwargs.pop('meta', None)
        assert self.__meta is not None
        Provider.__init__(self, self.__meta.provides)
        Array.__init__(self, type_identifier, members, **kwargs)


class Restricted(Encodable, Provider):

    @property
    def descriptor(self):
        """Return a :class:`Scalar` instance representing the descriptor."""
        return self.__meta.create_descriptor()

    @classmethod
    def frommeta(cls, meta, value):
        """Create a new :class:`Composite` using a :class:`.Meta`
        instance.
        """
        return cls(meta, value)

    def __init__(self, meta, encodable):
        self.__meta = meta
        self.__encodable = encodable
        Provider.__init__(self, meta.provides)
        Encodable.__init__(self, encodable.value)

    def as_dto(self):
        """Project the :class:`Encodable` as a Data Transfer Object (DTO)."""
        return self.__encodable.as_dto()

    def is_empty(self):
        """Return ``True`` if the :class:`Encodable` is empty."""
        # Restricted types are always scalar values, so never
        # empty.
        return False

    def get_source(self):
        """Return a string representing the source (primitive) AMQP type
        of the :class:`Encodable`.
        """
        return self.__meta.get_source()

    def __repr__(self):
        return repr(self.value)


TYPE_MAP = collections.defaultdict(lambda: Scalar, {
    'map': Map,
    'list': List,
    'array': Array
})


def encodable_factory(type_name, value, nd=None, sd=None, _in_array=False):
    """Create a new :class:`.Encodable` instance of the specified `type_name`
    containing `value`.
    """
    global TYPE_MAP
    if isinstance(value, list) and type_name not in ('array','list','map'):
        value = [encodable_factory(type_name, x, nd, sd, True) for x in value]
        type_name = 'array'
        nd = sd = None
    cls = TYPE_MAP[type_name]
    return cls.create(type_name, value, nd, sd, _in_array)

