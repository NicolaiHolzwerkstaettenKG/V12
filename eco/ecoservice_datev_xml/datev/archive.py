# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from uuid import UUID

from . import core
from .content import Content
from .header import Header


class Archive(core.XsdFile):

    def __init__(
        self,
        header: Header,
        content: Content,
        guid: UUID,
    ) -> None:
        self.filename = 'Document_v050'
        self.namespaces = {
            '': 'http://xml.datev.de/bedi/tps/document/v05.0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': (
                'http://xml.datev.de/bedi/tps/document/v05.0 '
                f'{self.filename}.xsd'
            ),
        }
        self.root_attr = {
            'xsi:schemaLocation': (
                'http://xml.datev.de/bedi/tps/document/v05.0 '
                f'{self.filename}.xsd'
            ),
        }
        self.data = {
            'archive': {
                '@version': '5.0',
                '@generatingSystem': 'ecoservice: Odoo DATEV XML',
                '@guid': guid,
                'header': header,
                'content': content,
            },
        }
