import functools

from amqp.factory import create_factory


class DataTransferObject(object):
    """Syntactic sugar to create Composite instances."""

    @classmethod
    def factory(cls, type_name):
        """Return a :class:`DataTransferObject` configured to produce
        objects of the given `type_name`.
        """
        return functools.partial(cls, type_name)

    def __init__(self, type_name, **params):
        self.type_name = type_name
        self.params = params
        self.factory = create_factory(self.type_name)

    def as_encodable(self):
        """Create an encodable object from the :class:`DataTransferObject`."""
        # Recursively visit the provided parameters to create amqp.Encodable
        # instances.
        params = {}
        for key in self.params.keys():
            value = self.params[key]
            if isinstance(value, DataTransferObject):
                value = value.as_encodable()
            params[key] = value
        return self.factory(**params)

    def __repr__(self):
        return "<DataTransferObject: {0}>".format(self.type_name)

