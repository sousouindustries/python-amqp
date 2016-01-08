from amqp.utils import compat


class Encoding(object):
    """Specifies the properties of an AMQP primitive type encoding."""

    def __init__(self, name, category, code, width):
        self.name = name
        self.category = category
        self.code = code
        self.width = width

    def can_encode(self, val):
        """Return ``True`` if the value fits in the :class:`Encoding`."""
        octets = 0

        # None is always encodable as NULL (0x40).
        if val is None:
            return True

        # Fixed types can either be integers types, floating point,
        # char (4 octet UTF32-BE encoded string), UUID, timestamp or
        # boolean.
        if self.category == 'fixed' and isinstance(val, compat.integer_types):
            octets = int(val.bit_length() / 8)

        # TODO
        return octets <= self.width
