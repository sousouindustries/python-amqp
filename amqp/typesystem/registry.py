import functools

from amqp.exc import DecodeError


REGISTRY = {}


def register(type_class, type_name, meta):
    REGISTRY[(type_class, type_name)] = meta


def get(type_class, identifier):
    """Return an AMQP type definition its `identifier`, which is a type
    name, format code or descriptor.
    """
    return REGISTRY[(type_class, identifier)]


register_type_name      = functools.partial(register, 'type_name')
register_format_code    = functools.partial(register, 'format_code')
register_descriptor     = functools.partial(register, 'descriptor')
get_by_type_name        = functools.partial(get, 'type_name')
get_by_descriptor       = functools.partial(get, 'descriptor')
get_by_format_code      = functools.partial(get, 'format_code')


def get_by_constructor(ctr):
    """Return an AMQP type definition using the constructor decoded from
    an incoming datastream.
    """
    try:
        if ctr.numeric:
            identifier = ('descriptor', ctr.numeric)
        elif ctr.symbolic:
            identifier = ('descriptor', ctr.symbolic)
        else:
            identifier = ('format_code', ctr.format_code)
        meta = get(*identifier)
    except LookupError:
        raise DecodeError("Unknown type: " + repr(identifier[1]))
    return meta
