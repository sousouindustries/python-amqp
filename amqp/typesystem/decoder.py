

def decode_null(format_code, value):
    assert value == b''
    return None


def decode_string(encoding, format_code, value):
    return value.decode(encoding)
