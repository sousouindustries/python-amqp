import warnings

from amqp.dto import DataTransferObject as DTO
from amqp.factory import create_factory
from amqp.typesystem import default_loader as loader
from amqp.typesystem import encodable_factory
from amqp.typesystem import encodable
from amqp.typesystem import Encoder
from amqp.typesystem import RawDecoder
from amqp.typesystem import SchemaDecoder
from amqp.typesystem import SchemaEncoder
from amqp.typesystem import parse_buffer


__all__ = [
    'create_object',
    'create_factory',
    'loader',
    'parse_buffer'
]


def get_version():
    return '1.0.0alpha13'
