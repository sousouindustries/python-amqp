from amqp.utils import compat


def decode_null(format_code, value):
    assert value == b''
    return None


def decode_string(encoding, format_code, value):
    return value.decode(encoding)


def decode_integer(signed, format_code, value):
    return compat.from_bytes(value, 'big', signed=signed)
