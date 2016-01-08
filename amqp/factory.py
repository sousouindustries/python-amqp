import copy

from amqp.typesystem.registry import get_by_type_name


class IFactory(object):
    """Base class for object factories."""
    type_name = None
    validators = None

    @classmethod
    def class_factory(cls, type_name, **attrs):
        """Create a new :class:`IFactory` implementation that produces objects
        of type `type_name`.
        """
        attrs['type_name'] = type_name
        return type('AMQPTypeFactory', (cls,), attrs)()

    def __init__(self):
        assert self.type_name is not None

    def create(self, *args):
        """Create an instance of the AMQP type specified by
        :attr:`type_name`.
        """
        meta = get_by_type_name(self.type_name)
        if meta.is_restricted():
            # Restricted types are always scalar, so the first
            # argument is the desired input value.
            args = args[0] if args else None
            if not args:
                args = [None]
        instance = meta.create(*args)
        self._run_validators(instance)
        return instance

    def validate(self, instance):
        """Hook to implement additional validation on an AMQP type
        instance.
        """

    def _run_validators(self, instance):
        for validate in (self.validators or []):
            validate(instance)
        self.validate(instance)

    def __call__(self, *args, **kwargs):
        return self.create(args or kwargs)



create_factory = IFactory.class_factory
