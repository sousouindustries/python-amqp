

class DecodeError(Exception):
    pass


class EncoderDoesNotExist(LookupError):
    pass


class DecoderDoesNotExist(DecodeError):
    pass


class SchemaSyntaxError(ValueError):
    pass


class ValidationError(Exception):
    pass
23.235.43.133
