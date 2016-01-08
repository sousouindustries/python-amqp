import functools

from amqp.const import NOT_PROVIDED
from amqp.exc import ValidationError
from amqp.typesystem.basetypes import Array
from amqp.typesystem.basetypes import Encodable
from amqp.typesystem.basetypes import Null
from amqp.typesystem.basetypes import Restricted
from amqp.typesystem.basetypes import RestrictedArray
from amqp.typesystem.registry import get_by_type_name
from amqp.typesystem.provider import Provider


class Field(object):

    def __init__(self, field_name, type_name, requires=None, mandatory=False,
        multiple=False, raw_default=None):
        """Initialize a new :class:`Field` instance."""
        self.field_name = field_name
        self.type_name = type_name
        self.requires = requires or set()
        self.mandatory = mandatory
        self.multiple = multiple
        self.raw_default = raw_default
        self.attname = field_name.replace('-','_')

    def clean(self, value):
        """Cleans an input value for an AMQP composite type field."""
        # If the field is mandatory, `value` may not be None or NOT_PROVIDED
        if value in (None, NOT_PROVIDED):
            if self.mandatory:
                raise ValidationError('required', self, value)

            # If the field is not mandatory, bail out early with a basetypes.Null
            # instance.
            return Null()

        # If the field specified its type name as "*", `value` is assumed to be
        # either a tuple of (type name, value) or a Provider which satisfied
        # the requirements of the field.
        if self.type_name == '*':
            if not isinstance(value, Provider):
                # Restricted types are provided as (type_name, value)
                assert len(value) == 2
                type_name, value = value
                meta = get_by_type_name(type_name)
                value = meta.create(value)\
                    if not self.multiple\
                    else self.clean_multiple(meta, value)

            self.clean_provider(value)
        else:
            meta = get_by_type_name(self.type_name)

        # If the field allows multiple values, the input value must be an a list
        # or an Array holding the members. Note that at this point, polymorphic
        # field types have already been casted to a Provider instance, for which
        # validation has already been done.
        if self.multiple and self.type_name != '*':
            members = value
            assert isinstance(value, list)

            # Array instances must be monomorphic, polymorphic collecions
            # are a validation error.
            if len(set(map(type, members))) > 1:
                raise ValidationError('polymorphic', self, members)

            value = Array.create('array', [meta.create(x) for x in members])

        elif not isinstance(value, Encodable):
            value = meta.create(value)

        # At this point, value MUST be an Encodable.
        assert isinstance(value, Encodable)
        return value

    def clean_provider(self, provider):
        """Cleans a restricted type."""
        # If the provider is an array with no members, there will be no
        # format code and no descriptor, so there is no need to validate
        # the provider. If there are members, validate the first member (
        # arrays are monomorphic, so all members will be valid).
        if isinstance(provider, Array):
            return True if provider.is_empty()\
                else self.clean_provider(provider[0])

        try:
            satisfies = provider.satisfies(self.requires)
        except AttributeError:
            satisfies = False
        if not satisfies:
            raise ValidationError('not_satisfied', self, provider)

    def clean_multiple(self, meta, members):
        """Cleans a field value which allows multiple values.

        Args:
            meta: the :class:`.Meta` describing the members.
            members: a list holding the members.

        Returns:
            Array
        """
        assert isinstance(members, list)

        # Array instances must be monomorphic, polymorphic collecions
        # are a validation error.
        if len(set(map(type, members))) > 1:
            raise ValidationError('polymorphic', self, members)

        members = Array.create('array', [meta.create(x) for x in members])

        # The Array object does not have a satisfies() method.
        # If the Meta instance specified a restricted type,
        # create a Restricted instance wrapping the array.
        if meta.is_restricted():
            members = RestrictedArray.frommeta(meta, members)

        return members

    def __repr__(self):
        return "<Field: {0} ({1})>".format(self.field_name, self.type_name)
