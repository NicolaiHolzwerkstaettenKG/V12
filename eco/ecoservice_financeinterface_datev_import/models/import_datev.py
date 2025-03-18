# Part of Odoo. Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE at the root directory of this module for full copyright and licensing details.

import base64
import csv
import io
import traceback
from datetime import datetime
from decimal import Decimal

from odoo import _, api, exceptions, fields, models


class ImportDatev(models.Model):
    _name = 'import.datev'
    _description = "Datev Import"

    name = fields.Char(
        readonly=True,
        default=lambda self: self.env['ir.sequence'].get(
            'datev.import.sequence'
        ) or '-',
    )
    description = fields.Char(required=True)
    company_id = fields.Many2one(
        comodel_name='res.company',
        string='Company',
        required=True,
        default=lambda self: self.env.company,
        domain=lambda self: self._get_allowed_companies_domain()
    )

    @api.model
    def _get_allowed_companies_domain(self):
        allowed_company_ids = self.env['res.company'].browse(self._context.get('allowed_company_ids', []))
        return [('id', 'in', allowed_company_ids.ids)]

    datev_ascii_file = fields.Binary(string='DATEV ASCII File')
    datev_ascii_filename = fields.Char(string='DATEV ASCII Filename')
    journal_id = fields.Many2one(
        comodel_name='account.journal',
        string='Journal',
        required=True
    )
    one_move = fields.Boolean(string='In one move?')
    log_line = fields.One2many(
        comodel_name='import.datev.log',
        inverse_name='parent_id',
        string='Log'
    )
    account_moves = fields.One2many(
        comodel_name='account.move',
        inverse_name='import_datev',
    )
    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('error', 'Error'),
            ('imported', 'Imported'),
            ('booking_error', 'Booking Error'),
            ('booked', 'Booked')
        ],
        string='Status', readonly=True, default='draft')

    # Extended configuration
    config_delimiter = fields.Char(string='Delimiter', size=1, default=';')
    config_quotechar = fields.Selection(string='Quote', selection=[('"', '"'), ("'", "'")], default='"')
    config_extended_datev_header = fields.Boolean(
        string='Extended Datev Header',
        default=True,
        help='The first line of a standard export from DATEV contains meta information.'
             ' If this is the case the line headers needed for the import are in the'
             ' second line and this option needs to be checked.'
    )
    config_encoding = fields.Selection(
        string='Encoding',
        selection=[
            ('utf_8', 'UTF-8'),
            ('latin_1', 'ISO-8859-1'),
            ('iso8859_15', 'ISO-8859-15'),
            ('cp1252', 'Windows-1252'),
        ],
        default='cp1252',
    )

    @api.onchange('datev_ascii_filename')
    def _onchange_datev_ascii_filename(self):
        if self.datev_ascii_filename:
            self.description = self.datev_ascii_filename

    def _lookup_erpvalue(self, field_config, value):
        """
        Get the ERP ID for the Object and the given Value.

        :param field_config: Dictionary of the field containing the erpobject and the erpfield
        :param value: Domain Search Value
        """
        value = False

        try:
            if field_config['erpfield'] == 'l10n_de_datev_code':
                if value in ['SD', '40']:
                    return value
                else:
                    try:
                        value = int(value)
                    except:  # noqa: E722
                        return False
            args = 'domain' in field_config and field_config['domain'] or []
            args.append((field_config['erpfield'], '=', value))
            value = self.env[field_config['erpobject']].search(args=args, limit=1)
        except:  # noqa: E722
            return False

        return value or False

    def convert_value(self, importcsv, import_config, import_struct, errorlist):
        """
        Convert given Value into the Datev Format.
        """
        data_list = []
        input_file = io.StringIO(importcsv.decode(encoding=import_config['encoding']))

        if import_config['extended_header']:
            datev_header = input_file.readline()

        importliste = csv.DictReader(
            input_file,
            delimiter=import_config['delimiter'],
            quotechar=import_config['quotechar'],
        )

        for linecounter, line in enumerate(importliste, start=1):
            spaltenvalues = {}

            for key in import_struct.keys():
                val = False
                csv_names = import_struct[key]['csv_name']
                try:
                    for csv_name in csv_names:
                        if csv_name in line and line[csv_name]:
                            if import_struct[key]['type'] == 'string':
                                val = line[csv_name]
                            elif import_struct[key]['type'] == 'integer':
                                val = int(
                                    line[csv_name]
                                )
                            elif import_struct[key]['type'] == 'decimal':
                                decimalvalue = line[csv_name]

                                if import_struct[key]['decimalformat'][0]:
                                    decimalvalue = decimalvalue.replace(
                                        import_struct[key]['decimalformat'][0], ''
                                    )
                                val = Decimal(decimalvalue.replace(
                                    import_struct[key]['decimalformat'][1], '.')
                                )

                            elif import_struct[key]['type'] == 'date':
                                dateformat = import_struct[key]['dateformat']
                                val = line[csv_name]
                                if '%y' not in dateformat and '%Y' not in dateformat:
                                    date_year = datev_header.split(';')[12].strip('"')[:4]
                                    dateformat += '-%Y'
                                    val += '-{date_year}'.format(date_year=date_year)

                                val = datetime.strptime(
                                    val, dateformat
                                ).date()

                            else:
                                errorlist.append({
                                    'line': linecounter,
                                    'name': _('Attribute type could not be resolved'),
                                    'beschreibung': _('Attribute type {type} could not be resolved!').format(
                                        type=import_struct[key]['type']
                                    )
                                })
                except:  # noqa: E722
                    errorlist.append({
                        'line': linecounter,
                        'name': _('Attribute could not be converted!'),
                        'beschreibung': _(
                            u"Attribute {name} in line {counter} could not be converted to type '{type}'!"
                        ).format(
                            name=import_struct[key]['csv_name'], counter=linecounter,
                            type=import_struct[key]['type'],
                        )
                    })
                if val:
                    spaltenvalues[key] = val
            data_list.append(spaltenvalues)
        ref = datev_header.split(';')[16].strip('"')
        return data_list, errorlist, ref

    def unlink(self):
        """
        Check if State is draft.
        """
        if any([s != 'draft' for s in self.mapped('state')]):
            raise exceptions.Warning(_('Import can only be deleted in state draft!'))
        return super(ImportDatev, self).unlink()

    def reset_import(self):
        """
        Reset the import.

        #. Unreconcile all reconciled imported Moves
        #. Cancel all imported moves not in state draft
        #. Delete all imported moves
        #. Delete all Importloglines
        #. Set Import state to draft
        """
        for datev_import in self:
            try:
                datev_import.account_moves.mapped('line_ids').filtered(
                    'reconciled').remove_move_reconcile()
                datev_import.account_moves.filtered(
                    lambda r: r.state != 'draft').button_cancel()
                datev_import.account_moves.with_context(force_delete=True).unlink()
                datev_import.log_line.unlink()
                datev_import.write({'state': 'draft'})
            except:  # noqa: E722
                self.log_line.create({
                    'parent_id': datev_import.id,
                    'name': _('Odoo ERROR: {error}').format(error=traceback.format_exc()),
                    'state': 'error',
                })
        return True

    def search_partner(self, konto):
        """
        Get the partner for the specified account.

        :param konto: ID of the account
        """
        sql = """SELECT id from res_partner where id in
                    (
                        SELECT split_part(res_id, ',', 2)::integer from ir_property
                        WHERE res_id like 'res.partner%'
                        and value_reference = 'account.account,{account_id}'
                    ) LIMIT 1;""".format(account_id=str(konto))  # nosec

        self.env.cr.execute(sql)  # nosec
        fetch = self.env.cr.fetchone()
        return fetch and int(fetch[0])

    def get_partner(self, line):
        """
        Search Partner for the line.

        :param line: Move Line
        """
        partner_id = False
        if line['konto_object'].account_type in ('receivable', 'payable'):
            partner_id = self.search_partner(line['konto_object'].id)
        if not partner_id:
            if line['gegenkonto_object'].account_type in ('receivable', 'payable'):
                partner_id = self.search_partner(line['gegenkonto_object'].id)
        return partner_id

    def get_import_defaults(self, datev_import):
        """
        Define default import_config and import_struct.
        """
        import_config = {
            'delimiter': str(datev_import.config_delimiter) or ';',
            'quotechar': str(datev_import.config_quotechar) or '"',
            'encoding': datev_import.config_encoding or 'utf_8',
            'extended_header': datev_import.config_extended_datev_header,
            'header_row': 1 + int(datev_import.config_extended_datev_header),
            'journal_id': datev_import.journal_id.id,
            'company_id': datev_import.company_id.id,
            'company_currency_id': datev_import.company_id.currency_id,
            'skonto_account': 499,
        }
        import_struct = {
            'gegenkonto': {
                'csv_name': ['Gegenkonto (ohne BU-Schlüssel)', 'Gegenkonto'],
                'csv_row': False,
                'type': 'string',
                'required': True,
                'erplookup': True,
                'erpobject': 'account.account',
                'erpfield': 'code',
                'domain': [],
                'zfill': 4,
            },
            'konto': {
                'csv_name': ['Konto', 'Kto'],
                'csv_row': False,
                'type': 'string',
                'required': True,
                'erplookup': True,
                'erpobject': 'account.account',
                'erpfield': 'code',
                'domain': [],
                'zfill': 4,
            },
            'wkz': {
                'csv_name': ['WKZ Umsatz'],
                'csv_row': False,
                'type': 'string',
                'required': False,
                'erplookup': True,
                'erpobject': 'res.currency',
                'erpfield': 'name',
            },
            'buschluessel': {
                'csv_name': ['BU-Schlüssel'],
                'csv_row': False,
                'type': 'string',
                'required': False,
                'erplookup': True,
                'erpobject': 'account.tax',
                'erpfield': 'l10n_de_datev_code'
            },
            'belegdatum': {
                'csv_name': ['Belegdatum'],
                'csv_row': False,
                'type': 'date',
                'required': True,
                'dateformat': '%d%m',
            },
            'beleg1': {
                'csv_name': ['Belegfeld 1'],
                'csv_row': False,
                'type': 'string',
                'required': False,
            },
            'beleg2': {
                'csv_name': ['Belegfeld 2'],
                'csv_row': False,
                'type': 'string',
                'required': False,
            },
            'umsatz': {
                'csv_name': ['Umsatz (ohne Soll/Haben-Kz)', 'Umsatz', 'Umsatz (ohne Soll-/Haben-Kennzeichen)'],
                'csv_row': False,
                'type': 'decimal',
                'required': True,
                'decimalformat': ('.', ',')
            },
            'kurs': {
                'csv_name': ['Kurs'],
                'csv_row': False,
                'type': 'decimal',
                'required': True,
                'decimalformat': ('.', ',')
            },
            'skonto': {
                'csv_name': ['Skonto'],
                'csv_row': False,
                'type': 'decimal',
                'required': False,
                'decimalformat': (False, ',')
            },
            'buchungstext': {
                'csv_name': ['Buchungstext', 'Butext'],
                'csv_row': False,
                'type': 'string',
                'required': False,
                'skipon': ['Gruppensumme', 'Abstimmsumme'],
            },
            'sollhaben': {
                'csv_name': ['Soll/Haben-Kennzeichen', 'Soll-/Haben-Kennzeichen', 'S/H'],
                'csv_row': False,
                'type': 'string',
                'required': True,
                'default': 'S'
            },
        }
        return import_config, import_struct

    def create_account_move(
            self, datev_import, import_config, line, linecounter, move_id=False, manual=False, title=None
    ):
        """
        Create the move for the import line.

        :param datev_import: Datev Import
        :param import_config: Import Config
        :param line: Move Line
        :param linecounter: Counter of the move line
        """
        partner_id = self.get_partner(line)

        if not move_id:
            if title:
                ref = title
            else:
                ref = ', '.join([x for x in [line.get('beleg1'), line.get('beleg2')] if x])
            move = {
                'import_datev': datev_import.id,
                'ref': ref,
                'journal_id': datev_import.journal_id.id,
                'company_id': import_config['company_id'],
                'date': line['belegdatum'],
                'ecofi_buchungstext': line.get('buchungstext', ''),
                'ecofi_manual': manual,
                'partner_id': partner_id,
            }
            move_id = self.account_moves.create(move)

        return move_id, partner_id

    def create_move_line_dict(self, move, import_config):
        move_line_dict = {
            'company_id': import_config['company_id'],
            'partner_id': move['partner_id'],
            'credit': str(move['credit']),
            'debit': str(move['debit']),
            'journal_id': import_config.get('journal_id', False),
            'account_id': move['account_id'],
            'date': move['date'],
            'name': move['name'],
            'move_id': move['move_id'],
            'ecofi_account_counterpart': move['ecofi_account_counterpart'],
            'ecofi_tax_id': move.get('ecofi_tax_id', False),
            'amount_currency': move.get('amount_currency', False),
            'date_maturity': move.get('date_maturity', False),
            'quantity': 1.0,
            'datev_posting_key': move.get('datev_posting_key', ''),
            'product_id': False,
            'tax_tag_ids': move.get('tax_tag_ids', False),
            'tax_ids': move.get('tax_ids', None),
            'display_type': move.get('display_type', False),
        }
        currency_id = move.get('currency_id', False)
        if currency_id:
            move_line_dict.update({
                'currency_id': currency_id,
            })
        return move_line_dict

    def compute_currency(self, move_line, line, import_config):
        cur = False
        if (type(line['wkz']) == int or str) and line['wkz'] != import_config['company_currency_id'].name:
            context = self.env.context.copy()
            context.update({'date': line['belegdatum'] or fields.Date.today()})
            if 'wkz' in line and line['wkz']:
                if type(line['wkz']) == int:
                    cur = self.env['res.currency'].search([('id', '=', line['wkz'])])
                if type(line['wkz']) == str:
                    cur = self.env['res.currency'].search([('name', '=', line['wkz'])])
            move_line['currency_id'] = cur[0].id if cur and cur[0] else cur
            move_line['amount_currency'] = move_line['debit'] - move_line['credit']

            if line.get('kurs', False):
                move_line['debit'] = Decimal(
                    str(
                        float(move_line['debit']) / float(line['kurs'])
                    ) if float(move_line['debit']) > 0 else 0
                )

                move_line['credit'] = Decimal(
                    str(
                        float(move_line['credit']) / float(line['kurs'])
                    ) if float(move_line['credit']) > 0 else 0
                )
        else:
            move_line['currency_id'] = import_config['company_currency_id'].id
            move_line['amount_currency'] = move_line['debit'] - move_line['credit']
        return move_line

    def create_main_lines(self, line, thismove, partner_id, import_config, import_struct, move_lines=None):
        """
        Create the Main booking Lines.

        :param line: Import Line
        :param thismove: MoveID
        :param move_lines: MoveLines
        """
        tax_id = None
        if move_lines is None:
            move_lines = []
        if not line.get('sollhaben'):
            line['sollhaben'] = import_struct['sollhaben']['default']
        if line['sollhaben'].upper() == 'S':
            debit = line.get('umsatz', Decimal('0.0'))
            credit = Decimal('0.0')
        else:
            debit = Decimal('0.0')
            credit = line.get('umsatz', Decimal('0.0'))
        gegenmove = {
            'credit': debit,
            'debit': credit,
            'account_id': line['gegenkonto_object'].id,
            'date': line['belegdatum'],
            'move_id': thismove,
            'name': line['buchungstext'],
            'partner_id': partner_id,
            'ecofi_account_counterpart': line['gegenkonto_object'].id,
            'display_type': 'payment_term',
        }
        mainmove = {
            'credit': credit,
            'debit': debit,
            'account_id': line['konto_object'].id,
            'date': line['belegdatum'],
            'move_id': thismove,
            'name': line['buchungstext'],
            'partner_id': partner_id,
            'ecofi_account_counterpart': line['gegenkonto_object'].id,
            'display_type': 'product',
        }

        if line.get('buschluessel') or line.get('konto_object') or line.get('gegenkonto_object'):
            # if not isinstance(line['buschluessel'], int):
            #     # We don't need the correction-key part of the booking key
            #     line['buschluessel'] = line['buschluessel'][-1]
            mainmove, gegenmove, taxmoves, tax_id = self.create_tax_line(
                mainmove,
                gegenmove,
                import_config,
                line
            )
            if tax_id:
                mainmove['tax_ids'] = [fields.Command.set(tax_id.ids)]

            if taxmoves:
                for taxmove in taxmoves:
                    move_lines.append(
                        self.compute_currency(
                            taxmove,
                            line,
                            import_config
                        )
                    )
        gegenmove = self.compute_currency(
            gegenmove,
            line,
            import_config
        )
        mainmove = self.compute_currency(
            mainmove,
            line,
            import_config
        )
        move_lines.append(
            self.create_move_line_dict(
                mainmove,
                import_config
            )
        )
        move_lines.append(
            self.create_move_line_dict(
                gegenmove,
                import_config
            )
        )
        return move_lines, tax_id

    def create_tax_line(self, mainmove, gegenmove, import_config, line):
        taxmoves = []
        tax_id = None

        user_type_list = self.env.ref(
            'account.selection__account_account__account_type__asset_receivable',
        ) + self.env.ref(
            'account.selection__account_account__account_type__liability_payable',
        )

        # Check account to Receivable or Payable
        konto_obj = line.get('konto_object', False)
        gegenkonto_obj = line.get('gegenkonto_object', False)
        if konto_obj and gegenkonto_obj:
            konto_obj_is_rec_or_pay = konto_obj.account_type in user_type_list
            gegenkonto_obj_is_rec_or_pay = gegenkonto_obj.account_type in user_type_list
            # check konto or gegenkonto is not receivable or payable
            if not konto_obj_is_rec_or_pay or not gegenkonto_obj_is_rec_or_pay:
                if konto_obj.datev_automatic_account and not tax_id:   # check konto automatic
                    tax_id = konto_obj.tax_ids[:1] or False
                elif gegenkonto_obj.datev_automatic_account and not tax_id:
                    # check gegenkonto automatic, when automatic, switch mainkonto with gegenkonto
                    tax_id = gegenkonto_obj.tax_ids[:1] or False
                    save_konto = mainmove
                    mainmove = gegenmove
                    gegenmove = save_konto

                elif line.get('buschluessel') and not tax_id:
                    if line['buschluessel'] in ['40', 'SD']:
                        mainmove['ecofi_bu'] = line['buschluessel']
                        mainmove['ecofi_tax_id'] = konto_obj.datev_tax_ids and konto_obj.datev_tax_ids[0].id or False
                        tax_id = None
                    else:
                        try:
                            buschluessel = int(line['buschluessel'])
                        except KeyError:
                            buschluessel = 0
                        tax_id = self.env['account.tax'].search(
                            [('l10n_de_datev_code', '=', buschluessel)],
                            limit=1,
                        )

        total = float(mainmove['debit'] + mainmove['credit'])

        if tax_id:
            # We need a tax object that has the right amount and the right calculation method
            # And because we do not want to create a new tax in the database we just create a
            # temporary tax object with the data of the tax with the corresponding booking key
            values = tax_id.copy_data()[0]
            values['price_include'] = True
            tmp_tax_id = tax_id.new(values)

            for tax in tmp_tax_id.compute_all(total).get('taxes'):
                if mainmove['credit'] == Decimal('0.00'):
                    tax_credit = 0.00
                    tax_debit = tax['amount']
                else:
                    tax_credit = tax['amount']
                    tax_debit = 0.00
                data = {
                    'move_id': mainmove['move_id'],
                    'name': ' '.join([x for x in [mainmove['name'], tax['name']] if x]),
                    'date': mainmove['date'],
                    'partner_id': mainmove['partner_id'],
                    'tax_ids': False,
                    'tax_tag_ids': tax['tag_ids'],
                    'account_id': tax['account_id'],
                    'credit': tax_credit,
                    'debit': tax_debit,
                    'ecofi_account_counterpart': line['gegenkonto_object'].id,
                    'display_type': 'tax',
                }
                mainmove['credit'] -= Decimal(str(data['credit']))
                mainmove['debit'] -= Decimal(str(data['debit']))
                taxmoves.append(data)

            # to giving the main move tax_tag_ids
            if mainmove.get('move_id').move_type in ['entry', 'out_invoice']:
                tax_tag_lines = tax_id.invoice_repartition_line_ids
            elif mainmove.get('move_id').move_type in ['out_refund']:
                tax_tag_lines = tax_id.refund_repartition_line_ids

            if tax_tag_lines:
                mainmove['tax_tag_ids'] = [
                    tag_id
                    for line in tax_tag_lines
                    if line.repartition_type != 'tax'
                    for tag_id in line.tag_ids.ids
                ]

        return mainmove, gegenmove, taxmoves, tax_id

    def do_import(self):
        """
        Import the Datev ASCII File Containing the Datev Moves.
        """
        errorlist = []
        for datev_import in self:
            import_config, import_struct = self.get_import_defaults(datev_import)
            self.reset_import()
            self.log_line.create({
                'parent_id': datev_import.id,
                'name': _('Import started!'),
                'state': 'info',
            })
            if datev_import.datev_ascii_file:
                importcsv = base64.decodebytes(datev_import.datev_ascii_file)
                vorlauf, errorlist, ref = self.convert_value(
                    importcsv,
                    import_config,
                    import_struct,
                    errorlist
                )
                if len(errorlist) == 0:
                    linecounter = 0
                    thismove = False
                    for line in vorlauf:
                        if 'buchungstext' in line and line['buchungstext'] in import_struct['buchungstext']['skipon']:
                            continue
                        linecounter += 1
                        try:
                            line['gegenkonto_object'] = self.env['account.account'].search([
                                ('code', '=', '{:04}'.format(int(line['gegenkonto']))),
                                ('company_id', '=', self.company_id.id)
                            ])
                            line['konto_object'] = self.env['account.account'].search([
                                ('code', '=', '{:04}'.format(int(line['konto']))),
                                ('company_id', '=', self.company_id.id)
                            ])
                        except:  # noqa: E722
                            raise exceptions.ValidationError(_(
                                'You have an incorrect file format.'
                                'Please change the Encoding field or upload a file with a correct format.'
                            ))
                        if not line['konto_object']:
                            errorlist.append({
                                'line': linecounter,
                                'name': _('Attribute could not be converted!'),
                                'beschreibung': _('Account {account} could not be found in Odoo!'.format(
                                    account=line['konto'],
                                ))
                            })
                        if not line['gegenkonto_object']:
                            errorlist.append({
                                'line': linecounter,
                                'name': _('Attribute could not be converted!'),
                                'beschreibung': _('Account {account} could not be found in Odoo!'.format(
                                    account=line['gegenkonto'],
                                ))
                            })

                        thismove = thismove if datev_import.one_move else False
                        manual = not datev_import.one_move
                        if not line.get('wkz', False):
                            currency_id = (
                                datev_import.journal_id.currency_id
                                or datev_import.company_id.currency_id
                            )
                            line['wkz'] = currency_id.id
                        if not errorlist:
                            thismove, partner_id = self.create_account_move(
                                datev_import,
                                import_config,
                                line,
                                linecounter,
                                move_id=thismove,
                                manual=manual,
                                title=ref
                            )
                            move_lines, tax_id = self.create_main_lines(
                                line,
                                thismove,
                                partner_id,
                                import_config,
                                import_struct
                            )

                            for move in move_lines:
                                move['credit'] = Decimal(move['credit'])
                                move['debit'] = Decimal(move['debit'])
                                move['move_id'] = move['move_id'].id

                            self.env['account.move.line'].create(move_lines)

                            self.log_line.create({
                                'parent_id': datev_import.id,
                                'name': _('Line: {line} has been imported').format(
                                    line=linecounter + import_config['header_row'],
                                ),
                                'state': 'standard',
                            })
                            datev_import.write({'state': 'imported'})
                        else:
                            for line in errorlist:
                                self.log_line.create({
                                    'parent_id': datev_import.id,
                                    'name': _('{desc} Line: {line}').format(
                                        desc=line['beschreibung'],
                                        line=line['line'],
                                    ),
                                    'state': 'error',
                                })
                            datev_import.write({'state': 'error'})
                else:
                    for line in errorlist:
                        self.log_line.create({
                            'parent_id': datev_import.id,
                            'name': _('{desc} Line: {line}').format(
                                desc=line['beschreibung'],
                                line=line['line']
                            ),
                            'state': 'error',
                        })
                    datev_import.write({'state': 'error'})
        return True

    def confirm_booking(self):
        """
        Confirm the booking after all moves have been imported.
        """
        for this_import in self:
            error = False
            for move in this_import.account_moves.filtered(lambda r: r.state == 'draft'):
                try:
                    move.action_post()
                    self.log_line.create({
                        'parent_id': this_import.id,
                        'name': _('{name} booked successful.').format(name=move.name),
                        'state': 'standard',
                    })
                except:  # noqa: E722
                    self.log_line.create({
                        'parent_id': this_import.id,
                        'name': _('{name} could not be booked, Odoo ERROR: {error}').format(
                            name=move.name,
                            error=traceback.format_exc(),
                        ),
                        'state': 'error',
                    })
                    error = True
            this_import.state = 'booking_error' if error else 'booked'
        return True
