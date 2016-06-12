from amqp.typesystem import const


class Compound(object):
    """Represents a compound datatype (array, mapping, list).

    Args:
        count: an unsigned integer specifying the number of members in
            the compound.
        members: an AMQP-encoded byte-sequence containing the members.
    """
    format_codes = None

    def __init__(self, count, members):
        assert self.format_codes is not None
        assert (count > 0 and bool(members)) or (count == 0 and not bool(members))
        self.count = count
        self.members = members


class Array(Compound):
    format_codes = None, const.ARRAY8, const.ARRAY32


class Mapping(Compound):
    format_codes = None, const.MAP8, const.MAP32


class List(Compound):
    format_codes = const.LIST0, const.LIST8, const.LIST32
