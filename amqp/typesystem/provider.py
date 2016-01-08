

class Provider(object):
    """Represents an AMQP type that provides archetypes (through the
    ``provides`` attribute.
    """

    @property
    def provides(self):
        return self.__provides

    def __init__(self, provides):
        self.__provides = provides

    def satisfies(self, requires):
        assert isinstance(requires, set)
        return requires & self.provides

