import os

from amqp.utils import compat
from amqp.typesystem.datastructures import TypeIdentifier
from amqp.typesystem.stream import decode_constructor
from amqp.typesystem.stream import is_collection
from amqp.typesystem.stream import is_variable
from amqp.typesystem.utils import get_type_length
from amqp.typesystem.utils import get_type_name


class Node(object):
    """A tree representing the AMQP-encoded byte-stream. The branches
    represent collection types, the leafs represent scalar types.
    """

    @property
    def format_code(self):
        return self.ctr.format_code

    @property
    def width(self):
        return self.ctr.width

    @property
    def type_identifier(self):
        return TypeIdentifier(
            type_name=get_type_name(self.ctr.format_code),
            symbolic=self.ctr.symbolic,
            numeric=self.ctr.numeric,
            members=None if not self.is_array() else\
                get_type_name(self.member_ctr.format_code)
        )

    @classmethod
    def frombuf(cls, buf, parent=None, ctr=None, depth=-1):
        start = buf.tell()
        if ctr is None:
            ctr = decode_constructor(buf.read)
        instance = cls(
            start, ctr,
            offset=buf.tell() - start,
            parent=parent,
            depth=depth
        )
        if is_collection(ctr.format_code):
            instance.set_members(buf)
        elif is_variable(ctr.format_code):
            instance.set_length(buf)
        else:
            instance.length = instance.width
            buf.seek(instance.width, os.SEEK_CUR)

        # If parent is None, this is the top-level node so reset
        # the buffer.
        #if parent is None:
        #    buf.seek(0)

        instance.end = buf.tell()
        return instance

    def __init__(self, start, ctr, offset=None, parent=None, depth=-1):
        """Initialize a new :class:`Node` instance."""
        self.ctr = ctr
        self.start= start
        self.end = None
        self.offset = offset
        self.member_size = None
        self.member_count = None
        self.member_ctr = None
        self.parent = parent
        self.children = []
        self.length = None
        self.depth = depth + 1

    def accept(self, visitor):
        """Accepts a visitor."""
        return visitor.visit(self)

    def is_array(self):
        """Return ``True`` if the :class:`Node` is an ``array``."""
        return self.format_code in (0xE0, 0xF0)

    def is_list(self):
        """Return ``True`` if the :class:`Node` is a ``list``."""
        return self.format_code in (0x45, 0xC0, 0xD0)

    def is_map(self):
        """Return ``True`` if the :class:`Node` is a ``map``."""
        return self.format_code in (0xC1, 0xD1)

    def set_length(self, buf):
        """Set the length of the variable-width encoding."""
        self.length = compat.from_bytes(buf.read(self.width), 'big')
        buf.seek(self.length, os.SEEK_CUR)

        # Update the offset with the length indicator.
        self.offset += self.width

    def set_members(self, buf):
        """Read the size and count indicator from the buffer."""
        self.member_size = compat.from_bytes(buf.read(self.width), 'big')
        self.member_count = compat.from_bytes(buf.read(self.width), 'big')

        start = buf.tell() - self.width
        if self.is_array():
            self.member_ctr = decode_constructor(buf.read)

        # Set the start of the members to the current buffer position
        # minus the width of the type length, because the total length
        # includes.
        end = start + self.member_size
        while buf.tell() < end:
            node = type(self).frombuf(
                buf,
                parent=self,
                ctr=self.member_ctr,
                depth=self.depth
            )
            self.children.append(node)
        assert buf.tell() == end, "{0}!={1}".format(buf.tell(), end)

    def is_scalar(self):
        """Return ``True`` if the :class:`Node` represents a scalar value
        i.e. it has no children.
        """
        return not bool(self.children)

    def value_from_buf(self, buf):
        """Return the AMQP-encoded value from the buffer."""
        assert self.is_scalar(),\
            "value_from_buf() can only be invoked on scalar values."
        buf.seek(self.start + self.offset)
        return buf.read(self.length)

    def __getitem__(self, key):
        return self.children[key]

    def __repr__(self):
        return "<Node: type={type} start={start} offset={offset} depth={depth}>".format(
            type=self.type_identifier.type_name,
            start=self.start,
            offset=self.offset,
            depth=self.depth
        )


def parse_buffer(buf):
    """Parse file-like object `buf` into a :class:`.Node` repressenting
    the AMQP-encoded tree in the datastream.
    """
    return Node.frombuf(buf)
