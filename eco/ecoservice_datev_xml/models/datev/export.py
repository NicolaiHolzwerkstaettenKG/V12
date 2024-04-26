# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import base64
import os
import shutil
import tempfile
from datetime import datetime
from zipfile import ZipFile

from odoo import _, exceptions, fields, models

from ...datev import (
    Archive,
    ClientName,
    ClientNumber,
    ConsultantNumber,
    Content,
    DateTime,
    Description40,
    Document,
    ExtensionFile,
    ExtensionInvoice,
    Header,
)


class DatevExport(models.Model):
    _inherit = 'datev.export'

    type = fields.Selection(  # noqa: A003
        selection_add=[
            ('xml_ledger', 'XML Ledger'),
            ('xml_invoice', 'XML Invoice'),
            ('xml_csv_extension', 'XML CSV extension'),
        ],
        ondelete={
            'xml_ledger': 'cascade',
            'xml_invoice': 'cascade',
            'xml_csv_extension': 'cascade',
        },
        default='xml_invoice',
    )

    date_from = fields.Date()
    date_to = fields.Date()

    def datev_archive_header(self) -> Header:
        client = self.company_id.l10n_de_datev_client_number
        consultant = self.company_id.l10n_de_datev_consultant_number
        return Header(
            date=DateTime(datetime.now()),
            description='DATEV Export',
            clientName=ClientName(self.company_id.name),
            clientNumber=ClientNumber(client),
            consultantNumber=ConsultantNumber(consultant),
        )

    def datev_archive_content(self, documents) -> Content:
        return Content(document=documents)

    def datev_archive(self, documents) -> Archive:
        return Archive(
            header=self.datev_archive_header(),
            content=self.datev_archive_content(documents),
            guid=self.uuid4,
        )

    def export(self) -> None:
        self.export_xml_ledger()
        self.export_xml_invoice()
        self.export_xml_csv_extension()
        super(DatevExport, self).export()

    def export_xml_ledger(self) -> None:
        """Generate DATEV XML ledger export ("Belegsatzdatendatei")."""
        if self.type != 'xml_ledger':
            return

        raise exceptions.UserError(_(
            'DATEV XML ledger export not implemented.'
        ))

    def export_xml_invoice(self) -> None:
        """Generate DATEV XML invoice export ("Rechnungsdatendatei")."""

        if self.type != 'xml_invoice':
            return

        moves = self.moves()
        if not moves:
            raise exceptions.UserError(_(
                'Nothing to export.'
            ))

        exportdir = f'{tempfile.gettempdir()}/datev/export/{self.id}'
        shutil.rmtree(exportdir, ignore_errors=True)
        os.makedirs(exportdir, exist_ok=True)
        documents = []

        for move in moves:
            move.get_uuid4()
            filename = f'{move.id}.xml'
            filepath = f'{exportdir}/{filename}'
            invoice = move.datev_invoice()
            if not invoice:
                # Invoices without taxes are skipped
                continue
            invoice.generate_xml(filepath=filepath)
            ext_xml = ExtensionInvoice(
                datafile=filename,
                property=move.datev_extension_property(),
            )

            files = move.datev_attachments(exportdir=exportdir)
            files.extend(self.add_expense_attachments(move, exportdir))
            if not files:
                # Atleast 1 file is required
                # https://apps.datev.de/help-center/documents/1007019
                continue
            extensions = [ExtensionFile(name=x) for x in files]
            extensions.insert(0, ext_xml)

            documents.append(Document(
                description=Description40(move.display_name),
                keywords=move.datev_keywords(),
                type=move.datev_document_type(),
                guid=move.uuid4,
                extension=extensions,
            ))

        if not documents:
            raise exceptions.UserError(_(
                'None of the invoices contain taxes. Nothing to export.'
            ))

        filepath = f'{exportdir}/document.xml'
        archive = self.datev_archive(documents)
        archive.generate_xml(filepath=filepath)
        self.zip_xml(exportdir)

    def export_xml_csv_extension(self) -> None:
        """Generate DATEV XML CSV attachment."""

        if self.type != 'xml_csv_extension':
            return

        moves = self.moves()
        if not moves:
            # No raise, extension might just be a non-invoice export
            return

        exportdir = f'{tempfile.gettempdir()}/datev/export/{self.id}'
        shutil.rmtree(exportdir, ignore_errors=True)
        os.makedirs(exportdir, exist_ok=True)
        documents = []

        for move in moves:
            move.get_uuid4()

            files: list = move.datev_attachments(exportdir=exportdir)
            files.extend(self.add_expense_attachments(move, exportdir))
            if not files:
                # Atleast 1 file is required
                # https://apps.datev.de/help-center/documents/1007019
                continue

            extensions = [ExtensionFile(name=x) for x in files]
            documents.append(Document(
                description=Description40(move.display_name),
                keywords=move.datev_keywords(),
                type=move.datev_document_type(),
                guid=move.uuid4,
                extension=extensions,
            ))

        if not documents:
            # No relevant attachments found.
            return

        filepath = f'{exportdir}/document.xml'
        archive = self.datev_archive(documents)
        archive.generate_xml(filepath=filepath)
        self.zip_xml(exportdir)

    def zip_xml(self, exportdir) -> None:
        zippath = f'{exportdir}.zip'
        with ZipFile(zippath, 'w') as f:
            for file in os.listdir(exportdir):
                f.write(f'{exportdir}/{file}', file)

        datas_file = open(zippath, 'rb')
        datas_content = datas_file.read()
        dateval = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        attachment = self.env['ir.attachment'].create({
            'name': f'{dateval}_{self.id}.zip',
            'res_model': 'datev.export',
            'res_id': self.id,
            'type': 'binary',
            'company_id': self.company_id.id,
            'datas': base64.b64encode(datas_content),
        })
        self.archive_id = attachment.id

        # Cleanup
        if os.path.exists(zippath):
            os.remove(zippath)
        shutil.rmtree(exportdir, ignore_errors=True)

    def add_expense_attachments(self, move, exportdir) -> list:
        res = []
        if not (move and exportdir and 'hr.expense.sheet' in self.env):
            return res

        expenses = self.env['hr.expense.sheet'].sudo()
        expenses = expenses.search([('account_move_id', '=', move.id)])
        for expense in expenses:
            attach = expense.expense_line_ids.message_main_attachment_id
            res.extend(move.datev_attachments(
                exportdir=exportdir,
                attachments=attach,
            ))
        return res
