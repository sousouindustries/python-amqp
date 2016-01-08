

class Encodable(object):
    """Represents an object that can be encoded to an AMQP bytestream
    by invoking ``__bytes__`` or ``bytes(instance)``.
    """

    def to_bytes(self):
        raise NotImplementedError("Subclasses must override this method.")

    def __bytes__(self):
        return self.to_bytes()
