from amqp.typesystem import decoder
from amqp.typesystem import encoder
from amqp.typesystem import Described


class AMQPCodec(object):

    def encode(self, value):
        """Encode `value` to the AMQP 1.0 data format. Return a byte-sequence.

        If `value` is a native Python datatype, try to guess the appropriate
        AMQP format using various heuristics.

        If `value` is an instance of :class:`~amqp.typesystem.described.Described`,
        encode using the constructor and encoder specified.

        If `value` is a subclass of :class:`amqp.mixins.Encodable`, invoke it's
        :meth:`~amqp.mixins.Encodable.encode()` method.

        Args:
            value: the value to encode.

        Returns:
            byte-sequence
        """
