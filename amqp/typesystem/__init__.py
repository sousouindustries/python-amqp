import os

from amqp.typesystem.basetypes import encodable_factory
from amqp.typesystem.decoder import RawDecoder
from amqp.typesystem.decoder import SchemaDecoder
from amqp.typesystem.encoder import Encoder
from amqp.typesystem.encoder import SchemaEncoder
from amqp.typesystem.loader import SchemaLoader
from amqp.typesystem.node import parse_buffer
from amqp.typesystem import registry


__all__ = [
    'encodable_factory',
    'parse_buffer',
    'load_schema',
    'load_xml'
]



default_loader = SchemaLoader(registry)
load_schema = default_loader.load_file
load_xml = default_loader.load_xml
load_schema(os.path.join(os.path.dirname(__file__), 'types.xml'))
load_schema(os.path.join(os.path.dirname(__file__), 'transport.xml'))


def encodable(type_name, value):
    """Create a new :class:`.Composite` or :class:`.Restricted` instance."""
    meta = registry.get_by_type_name(type_name)
    return meta.create(value)
