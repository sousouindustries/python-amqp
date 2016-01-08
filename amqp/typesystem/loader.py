import os
import glob
import xml.etree.ElementTree as xml

from amqp.typesystem.meta import Meta
from amqp.typesystem.utils import strip_namespace


class SchemaLoader(object):
    """Loads AMQP type definitions from XML documents."""

    def __init__(self, registry):
        self.registry = registry

    def load_file(self, filepath, **kwargs):
        """Loads an XML document from `filepath` and imports the declared
        AMQP type definitions.
        """
        with open(filepath) as f:
            stream = f.read()
        return self.load_xml(stream, **kwargs)

    def load_xml(self, document, **kwargs):
        """Parses XML document `document` and imports the declared AMQP
        type definitions.
        """
        document = strip_namespace(document)
        root = xml.fromstring(document)
        elements = (root.findall('.//type') + root.findall('.//definition'))
        for element in elements:
            self.load_element(element)

    def load_element(self, element):
        """Loads an AMQP type definition from an XML element, which
        may be a ``type`` or a ``definition`` element.
        """
        if element.tag == 'type':
            self.load_type(element)
        elif element.tag == 'definition':
            self.load_definition(element)
        else:
            raise NotImplementedError("Unknown element: " + element.tag)

    def load_type(self, element):
        """Imports an AMQP type definition."""
        meta = Meta.fromelement(self.registry, element)

    def load_definition(self, element):
        """Imports an AMQP constant definition."""
        pass


