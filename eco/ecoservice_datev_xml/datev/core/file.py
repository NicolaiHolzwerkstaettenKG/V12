# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import os
from xml.etree import ElementTree  # nosec B405

from xmlschema import BadgerFishConverter, XMLSchema, from_json

from . import XsdComplexType

datev_path = f'{os.path.join(os.path.dirname(__file__))}/..'


class XsdFile(XsdComplexType):
    namespaces: dict = {}
    root_attr: dict = {}
    filename: str = None

    def filepath(self) -> str:
        """Return path to xsd file."""
        if not self.filename:
            return None
        return f'{datev_path}/xsd/{self.filename}.xsd'

    def schema(self) -> XMLSchema:
        """Return required schema."""
        if not self.filename:
            return None
        return XMLSchema(
            self.filepath(),
            converter=BadgerFishConverter,
        )

    def generate_xml(self, filepath) -> None:
        xml_tree = from_json(
            source=self.json_data(),
            schema=self.schema(),
            preserve_root=True,
            namespaces=self.namespaces,
            validation='strict',
            converter=BadgerFishConverter,
        )
        open(filepath, 'w+').close()
        xml_tree.attrib.update(self.root_attr)
        ElementTree.ElementTree(xml_tree).write(
            filepath,
            encoding='UTF-8',
            xml_declaration=True,
        )
        self.remove_xml_namespace(filepath=filepath)

    def remove_xml_namespace(self, filepath):
        texts = ''
        with open(filepath, 'r+') as text_file:
            texts = text_file.read()
            texts = texts.replace(':ns0', '').replace('ns0:', '')
        with open(filepath, 'wb') as text_file:
            # DATEV only supports ascii chars
            text_file.write(texts.encode('ascii', errors='ignore'))
