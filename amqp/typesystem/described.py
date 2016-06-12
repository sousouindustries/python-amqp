

class Described(object):
    """A wrapper class that is used to instruct the encoder to use
    a specific format code and an optional descriptor. Note that this
    may raise an exception during encoding if the format code is not
    appropriate for the given value.
    """

    def __init__(self, format_code, value, descriptor=None):
        self.format_code = format_code
        self.value = value
        self.descriptor = descriptor
