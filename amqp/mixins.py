

class Encodable(object):
    """Specifies the base interface for objects that are encodable by
    the :class:`~amqp.codec.codec.AMQPCodec`.
    """

    def encode(self, codec):
        """Encode the object to a byte-sequence."""
        raise NotImplementedError("Subclasses must override this method.")
