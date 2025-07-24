# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

import re
from decimal import Decimal
from typing import Tuple as TTuple
from odoo import api, models


class Ecofi(models.Model):
    _name = 'ecofi'
    _inherit = ['ecofi', 'ecofi.export.columns']

    def field_config(  # noqa: C901
        self,
        move,
        line,
        errorcount,
        partnererror,
        thislog,
        thismovename,
        faelligkeit,
        datevdict,
    ):

        """
        Generate the values for the different Datev columns.

        :param move: account_move
        :param line: account_move_line
        :param errorcount: Errorcount
        :param partnererror: Partnererror
        :param thislog: Log
        :param thismovename: Movename
        :param faelligkeit: Fälligkeit
        """
        # Übersetzung des Journaltyps
        journal_type_translation = dict(
            move.journal_id._fields['type']._description_selection(self.env)
        ).get(move.journal_id.type)

        # 111632 "Datev Export: Buchungsdatum und Belegdatum"
        # Im Meeting vom 24.06.25 um 14:30 wurde durch Falk, Simon und Jan final
        # beschlossen, dass das Feld "date" immer als Buchungsdatum und Belegdatum
        # verwendet wird - wie im Odoo Standard. Alles andere ist eine Abweichung vom
        # Odoo Standard UND vom DATEV Standard und wird somit NICHT mehr unterstützt.
        datevdict['Belegdatum'] = move.date.strftime('%d%m')  # Do not change!
        datevdict['Steuerperiode'] = move.date.strftime('%d%m%Y')

        # Standard
        datevdict['Beleg1'] = move.name

        # Kundenzahlung
        if move.journal_id.type == 'bank':
            payment_ids = move.line_ids.mapped('payment_id')
            reconciled_ids = payment_ids.mapped('reconciled_invoice_ids')

            if not payment_ids:
                datevdict['Buchungstext'] = move.display_name
                # compare line name with move_name
                if line.name and line.move_name:
                    if line.name != line.move_name:
                        datevdict['Beleg1'] = line.name
                        datevdict['Buchungstext'] = line.move_name
            else:
                if reconciled_ids:
                    datevdict['Buchungstext'] = datevdict['Beleg1']
                    invoice_names = []
                    for reconciled_id in reconciled_ids:
                        invoice_names.append(reconciled_id.name)
                    datevdict['Beleg1'] = ', '.join(invoice_names)
                elif move.ref:
                    datevdict['Buchungstext'] = datevdict['Beleg1']
                    datevdict['Beleg1'] = move.ref

        # Kundenrechnung
        elif move.journal_id.type == 'sale':
            if move.name:
                datevdict['Beleg1'] = move.name
                datevdict['Buchungstext'] = move.name

        elif move.journal_id.type == 'purchase' and move.ref:
            datevdict['Beleg1'] = move.ref

        if faelligkeit:
            datevdict['Beleg2'] = faelligkeit

        if move.ecofi_buchungstext:
            datevdict['Buchungstext'] = move.ecofi_buchungstext

        if line.name and line.name not in ['/', '<p><br></p>', '<p><br/></p>']:
            line_name = (
                line.name
                    .replace('<p>', '')
                    .replace('</p>', '')
                    .replace('<br/>', '')
                    .replace('<br>', '')
                    .replace('[', '(')
                    .replace(']', ')')
                    .replace('\t', ' ')
            )

            if datevdict.get('Buchungstext'):
                datevdict['Buchungstext'] = '{m_bu}, {l_bu}'.format(
                    m_bu=datevdict['Buchungstext'],
                    l_bu=line_name,
                )
            else:
                datevdict['Buchungstext'] = line_name

        datevdict = self.set_country_code(
            datevdict=datevdict,
            move=move,
        )

        if line.account_id.datev_vat_handover and line.ecofi_tax_id:
            datevdict['EUSteuer'] = str(
                line.ecofi_tax_id.amount
            ).replace('.', ',')

        module_oss = self.env['ir.module.module'].search(
            [('name', '=', 'l10n_eu_oss')],
            limit=1
        )
        if module_oss and module_oss.state == 'installed':
            if line.ecofi_tax_id:
                oss_found = (
                    'OSS' in line.ecofi_tax_id.tax_group_id.name and any(
                        'OSS' in tag.name for tag in line.ecofi_tax_id.invoice_repartition_line_ids.tag_ids
                    )
                )
                if oss_found:
                    datevdict['EUSteuer'] = str(
                        line.ecofi_tax_id.amount
                    ).replace('.', ',')

        if line.partner_id:
            datevdict['ZusatzInhalt1'] = line.partner_id.name

        if datevdict.get('ZusatzInhalt1'):
            datevdict['Zusatzinformation - Art 1'] = journal_type_translation or '-'

        # set values for Beleginfo to bill information
        if (
            (move.journal_id and move.journal_id.type in ['purchase'])
            and line.move_id
        ):
            datevdict['BelegInfoArt1'] = 'Odoo Bill no'
            datevdict['BelegInfoInhalt1'] = line.move_id.name

        # add code of analytic account to kost1 and kost2
        datevdict = self._get_analytic_account_datev(datevdict, line)

        # delivery date
        if (
            self.env.user.company_id.export_delivery_date
            and move.move_type == 'in_invoice'
            and move.date
        ):
            datevdict['Leistungsdatum'] = move.date.strftime('%d%m%Y')
        if (
            self.env.user.company_id.export_delivery_date
            and move.move_type == 'out_invoice'
            and move.delivery_date
        ):
            datevdict['Leistungsdatum'] = move.delivery_date.strftime('%d%m%Y')

        # beleglink
        move, line, datevdict = self.set_beleglink(move, line, datevdict)
        return errorcount, partnererror, thislog, thismovename, datevdict

    def get_country_code(self, partner, lines) -> str:
        res = ''
        if not partner:
            return res

        if partner.country_id:
            res = partner.country_id.code

        if any(lines.mapped('account_id.datev_vat_handover')) and partner.vat:
            res = partner.vat

        # Task 110088: Handle exceptions from ISO-Code 3166
        if res == 'GR':
            res = 'EL'
        elif res == 'IE':
            res = 'XI'

        return res

    def set_country_code(self, datevdict, move):
        datevdict['EulandUSTID'] = self.get_country_code(
            move.partner_id,
            lines=move.line_ids,
        )
        return datevdict

    def _get_analytic_account_datev(self, datevdict, line):
        code1 = code2 = ''
        if 'analytic_distribution' in line and line.analytic_distribution:
            a_dist = line.analytic_distribution
            for k, v in sorted(a_dist.items(), key=lambda item: (-item[1], item[0])):
                analytic_account = self.env['account.analytic.account'].browse(int(k))
                if analytic_account.code:
                    if not code1:
                        code1 = analytic_account.code
                    elif not code2:
                        code2 = analytic_account.code
        datevdict['Kost1'] = code1
        datevdict['Kost2'] = code2
        return datevdict

    def set_beleglink(self, move, line, datevdict):
        return move, line, datevdict

    def format_umsatz(self, lineumsatz):
        """
        Return the formatted amount.

        :param lineumsatz: amountC
        """
        soll_haben = 's' if lineumsatz > 0 else 'h'
        umsatz = str(abs(lineumsatz)).replace('.', ',')
        return umsatz, soll_haben

    def generate_csv(self, ecofi_csv, bookingdict, log):
        """
        Implement the generate_csv method for the datev interface.
        """
        ecofi_csv.writerow(bookingdict['datevheader'])
        ecofi_csv.writerow(bookingdict['buchungsheader'])
        for buchungsatz in bookingdict['buchungen']:
            ecofi_csv.writerow(buchungsatz)
        return super().generate_csv(ecofi_csv, bookingdict, log)

    def generate_csv_move_lines(  # noqa: C901
        self,
        move,
        buchungserror,
        errorcount,
        thislog,
        thismovename,
        export_method,
        partnererror,
        buchungszeilencount,
        bookingdict
    ):
        """
        Implement the generate_csv_move_lines method for the datev interface.
        """
        # Set Headers
        if 'buchungen' not in bookingdict:
            bookingdict['buchungen'] = []
            bookingdict['buchungsheader'] = (
                self.env['ecofi.export.columns'].get_datev_column_headings()
            )
            bookingdict['datevheader'] = (
                self.get_legal_datev_header(move.vorlauf_id)
            )

        return self.generate_csv_move_lines_v1(
            move,
            buchungserror,
            errorcount,
            thislog,
            thismovename,
            export_method,
            partnererror,
            buchungszeilencount,
            bookingdict
        )

    def has_equal_kost_columns(self, product_lines) -> bool:
        """Return if all product lines share the same analytic distribution"""

        if 'analytic_distribution' not in product_lines:
            # Feature disabled in settings
            return True

        line_dicts = product_lines.mapped('analytic_distribution')
        if len(line_dicts) == 1:
            return True

        line_dicts = product_lines.mapped('analytic_distribution')

        # Each move line contains a dict in the field "analytic_distribution"
        # with the base template "{'<aaa_id>': <distr. percentage>}"
        first = None
        for line_dict in line_dicts:
            lkeys = False
            if isinstance(line_dict, dict):
                lkeys = line_dict.keys()
            if first is None:
                first = lkeys
                continue
            if first != lkeys:
                return False
        return True

    def get_grouped_kost_columns(self, product_lines) -> TTuple[str, str]:
        # Einstellungen -> Buchungszeilen -> Kostenrechnung
        if 'analytic_distribution' not in product_lines:
            # Feature disabled in settings
            return '', ''

        aaa_ids = []
        line_dicts = product_lines.mapped('analytic_distribution')

        # Each move line contains a dict in the field "analytic_distribution"
        # with the base template "{'<aaa_id>': <distr. percentage>}"
        for line_dict in line_dicts:
            if not line_dict:
                # Skip product lines without analytic distributions
                continue
            for aaa_id in line_dict.keys():
                aaa_ids.append(int(aaa_id))

        aaa = self.env['account.analytic.account'].sudo().browse(aaa_ids)
        dist_codes = [x.code for x in aaa if x and x.code]

        if not dist_codes:
            return '', ''
        if len(dist_codes) > 1:
            return dist_codes[0], dist_codes[1]
        return dist_codes[0], ''

    def generate_grouped_csv_move_lines(  # noqa: C901
        self,
        move,
        buchungserror,
        errorcount,
        thislog,
        thismovename,
        export_method,
        partnererror,
        buchungszeilencount,
        bookingdict
    ):
        lines = move.line_ids
        company = move.company_id or self.env.company

        # Get relevant line types
        # Respect odoo standard or atleast comment changes to it properly
        tax_lines = lines.filtered(lambda x: x.display_type == 'tax')
        product_lines = lines.filtered(lambda x: x.display_type == 'product')
        term_lines = lines.filtered(lambda x: x.display_type == 'payment_term')

        move_account_id = product_lines.mapped('account_id')
        move_counter_account_id = product_lines.mapped(
            'ecofi_account_counterpart'
        )
        if len(move_account_id) != 1 or len(move_counter_account_id) != 1:
            # Too many accounts for same invoice/batch. Can't export
            # a grouped invoice/batch
            return False

        account_code = (
            move_account_id
            and move_account_id.code
            or ''
        )
        counter_account_code = (
            move_counter_account_id
            and move_counter_account_id.code
            or ''
        )

        # Get taxes
        tax_ids = lines.mapped('tax_ids')
        if not (
            company.datev_group_lines
            and len(tax_ids) == 1
            and len(move_account_id) == 1
            and self.has_equal_kost_columns(product_lines=product_lines)
        ):
            return None

        # Gross
        base_balance = sum(term_lines.mapped('balance'))
        base_balance = -base_balance if base_balance < 0 else base_balance
        base_currency = move.company_currency_id
        foreign_balance = move.amount_total_in_currency_signed
        foreign_currency = move.currency_id
        sollhaben = 'h' if base_balance < 0 else 's'
        exchange_rate = 0
        for line in product_lines:
            exchange_rate += line._currency_exchange_rate()

        if company.datev_ignore_currency:
            # Foreign and base currency is the same or the customer doesn't
            # want to export foreign currencies.
            foreign_balance = base_currency
            foreign_balance = base_balance
            exchange_rate = ''
            base_currency = ''
            base_balance = ''

        booking_key = tax_ids.mapped('l10n_de_datev_code')
        booking_key = booking_key[0] if booking_key else ''

        export_date = move.date
        if move.invoice_date:
            export_date = move.invoice_date
        export_date = export_date.strftime('%d%m')

        date_maturity = term_lines.mapped('date_maturity')
        if date_maturity:
            date_maturity = date_maturity[0].strftime('%d%m%y')

        booking_text = '{:.55}'.format(
            ', '.join([x for x in term_lines.mapped('name') if x])
        )
        receipt_link = '{link_type} ""{link}""'.format(
            link_type=company.export_document_link_type.upper(),
            link=move.get_uuid4(),
        )

        receiptInfoType1 = ''
        receiptInfoContent1 = ''
        if move.journal_id and move.journal_id.type in ['purchase']:
            receiptInfoType1 = 'Odoo Bill no'
            receiptInfoContent1 = move.name

        kost1, kost2 = self.get_grouped_kost_columns(product_lines)

        # EU Tax
        ecofi_tax_ids = lines.mapped('ecofi_tax_id')
        handovers = lines.mapped('account_id.datev_vat_handover')
        eu_tax = ''
        if any(handovers) and ecofi_tax_ids:
            eu_tax = str(
                sum(ecofi_tax_ids.mapped('amount'))
            ).replace('.', ',')

        # Leistungsdatum
        service_date = move.date.strftime('%d%m%Y')
        if (
            company.export_delivery_date
            and move.move_type == 'out_invoice'
            and move.delivery_date
        ):
            service_date = move.delivery_date.strftime('%d%m%Y')

        # Tax Period
        tax_period = move.date and move.date.strftime('%d%m%Y') or ''

        # Only export positive values
        if base_balance and base_balance < 0:
            base_balance = -base_balance
        if foreign_balance and foreign_balance < 0:
            foreign_balance = -foreign_balance

        bookingdict['move_bookings'].append([
            str(foreign_balance).replace('.', ','),  # Umsatz
            sollhaben,
            foreign_currency.name if foreign_currency else '',
            exchange_rate or '',
            str(base_balance).replace('.', ','),  # Basiswaehrungsbetrag
            base_currency.name if base_currency else '',
            account_code,
            counter_account_code,
            booking_key,
            export_date,
            move.name,  # Beleg1
            date_maturity or '',
            '',  # Skonto
            booking_text,
            '',  # Postensperre
            '',  # Diverse Adressnummer
            '',  # Geschäftspartnerbank
            '',  # Sachverhalt
            '',  # Zinssperre
            receipt_link or '',  # Beleglink
            receiptInfoType1,  # Beleginfo - Art 1
            receiptInfoContent1,  # Beleginfo - Inhalt 1
            '',  # Beleginfo - Art 2
            '',  # Beleginfo - Inhalt 2
            '',  # Beleginfo - Art 3
            '',  # Beleginfo - Inhalt 3
            '',  # Beleginfo - Art 4
            '',  # Beleginfo - Inhalt 4
            '',  # Beleginfo - Art 5
            '',  # Beleginfo - Inhalt 5
            '',  # Beleginfo - Art 6
            '',  # Beleginfo - Inhalt 6
            '',  # Beleginfo - Art 7
            '',  # Beleginfo - Inhalt 7
            '',  # Beleginfo - Art 8
            '',  # Beleginfo - Inhalt 8
            kost1 or '',
            kost2 or '',
            '',  # Kostmenge,
            self.get_country_code(move.partner_id, lines),  # EulandUSTID
            eu_tax,  # EUSteuer
            '',  # Abw. Versteuerungsart
            '',  # Sachverhalt L+L
            '',  # Funktionsergänzung L+L
            '',  # BU 49 Hauptfunktionstyp
            '',  # BU 49 Hauptfunktionsnummer
            '',  # BU 49 Funktionsergänzung
            '',  # Zusatzinformation - Art 1
            '',  # Zusatzinformation- Inhalt 1
            '',  # Zusatzinformation - Art 2
            '',  # Zusatzinformation- Inhalt 2
            '',  # Zusatzinformation - Art 3
            '',  # Zusatzinformation- Inhalt 3
            '',  # Zusatzinformation - Art 4
            '',  # Zusatzinformation- Inhalt 4
            '',  # Zusatzinformation - Art 5
            '',  # Zusatzinformation- Inhalt 5
            '',  # Zusatzinformation - Art 6
            '',  # Zusatzinformation- Inhalt 6
            '',  # Zusatzinformation - Art 7
            '',  # Zusatzinformation- Inhalt 7
            '',  # Zusatzinformation - Art 8
            '',  # Zusatzinformation- Inhalt 8
            '',  # Zusatzinformation - Art 9
            '',  # Zusatzinformation- Inhalt 9
            '',  # Zusatzinformation - Art 10
            '',  # Zusatzinformation- Inhalt 10
            '',  # Zusatzinformation - Art 11
            '',  # Zusatzinformation- Inhalt 11
            '',  # Zusatzinformation - Art 12
            '',  # Zusatzinformation- Inhalt 12
            '',  # Zusatzinformation - Art 13
            '',  # Zusatzinformation- Inhalt 13
            '',  # Zusatzinformation - Art 14
            '',  # Zusatzinformation- Inhalt 14
            '',  # Zusatzinformation - Art 15
            '',  # Zusatzinformation- Inhalt 15
            '',  # Zusatzinformation - Art 16
            '',  # Zusatzinformation- Inhalt 16
            '',  # Zusatzinformation - Art 17
            '',  # Zusatzinformation- Inhalt 17
            '',  # Zusatzinformation - Art 18
            '',  # Zusatzinformation- Inhalt 18
            '',  # Zusatzinformation - Art 19
            '',  # Zusatzinformation- Inhalt 19
            '',  # Zusatzinformation - Art 20
            '',  # Zusatzinformation- Inhalt 20
            '',  # Stück
            '',  # Gewicht
            '',  # Zahlweise
            '',  # Forderungsart
            '',  # Veranlagungsjahr
            '',  # Zugeordnete Fälligkeit
            '',  # Skontotyp
            move.invoice_origin or '',  # Auftragsnummer
            '',  # Buchungstyp
            '',  # Ust-Schlüssel (Anzahlungen)
            '',  # EU-Land (Anzahlungen)
            '',  # Sachverhalt L+L (Anzahlungen)
            '',  # EU-Steuersatz (Anzahlungen)
            '',  # Erlöskonto (Anzahlungen)
            '',  # Herkunft-Kz
            '',  # Leerfeld
            '',  # KOST-Datum
            '',  # Mandatsreferenz
            '',  # Skontosperre
            '',  # Gesellschaftername
            '',  # Beteiligtennummer
            '',  # Identifikationsnummer
            '',  # Zeichnernummer
            '',  # Postensperre bis
            '',  # Bezeichnung SoBil-Sachverhalt
            '',  # Kennzeichen SoBil-Buchung
            str(int(bool(
                move.restrict_mode_hash_table and move.inalterable_hash
            ))),  # Festschreibung
            service_date,  # Leistungsdatum
            tax_period  # Datum Zuord.Steuerperiode
        ])

        return (
            buchungserror,
            errorcount,
            thislog,
            partnererror,
            buchungszeilencount,
            bookingdict,
            tax_lines
        )

    def generate_csv_move_lines_v1(  # noqa: C901
        self,
        move,
        buchungserror,
        errorcount,
        thislog,
        thismovename,
        export_method,
        partnererror,
        buchungszeilencount,
        bookingdict
    ):
        company = move.company_id or self.env.company
        faelligkeit = False
        move_tax_lines = 0
        grouped_line = {}
        cash_basis = company.tax_cash_basis_journal_id
        tax_exigibility = company.tax_exigibility
        rounding_method = company.tax_calculation_rounding_method

        move = self._prepare_move(move, export_method)
        ignore_currency = self.env.context.get('datev_ignore_currency')

        for line in move.line_ids:
            if line.debit == 0 and line.credit == 0:
                continue
            datevkonto = line.account_id.code
            datevgegenkonto = line.ecofi_account_counterpart.code
            if datevgegenkonto == datevkonto:
                if line.date_maturity:
                    faelligkeit = line.date_maturity.strftime('%d%m%y')
                continue

            sollhaben = 'h' if line.balance < 0 else 's'

            # 110646 "Export von Fremdwährung"
            # Keine Rechnungsbeträge verwenden! Nur Buchungsbeträge.
            # Da Rechnungsbeträge NUR bei Rechnungen gesetzt werden.
            base_currency = line.company_currency_id or company.currency_id
            foreign_currency = line.currency_id
            exchange_rate = line._currency_exchange_rate()

            # 110851 "Minus im Export"
            # line.balance kann negativ sein.
            # line.amount_currency kann negativ sein.
            # In Odoo ist negativ richtig, im Export positiv.
            base_currency_untaxed = Decimal(line.credit or line.debit)
            foreign_currency_untaxed = Decimal(
                line.amount_currency
                if line.amount_currency >= 0
                else line.amount_currency * -1
            )

            tax = line.get_tax()
            tax_multiplier = 1 + (Decimal(tax.amount) / 100)
            tax_repartitions = tax.invoice_repartition_line_ids

            if line.is_refund:
                # Wenn Refund, nutze Refund-Steuerzeilen
                tax_repartitions = tax.refund_repartition_line_ids

            if tax_repartitions and len(tax_repartitions) > 2:
                # Steuern die einen Buchungssatz mit mehreren Steuern erzeugen,
                # sollen auf 0 gesetzt werden. Aufgabe 110719
                tax_multiplier = 1

            base_currency_taxed = base_currency_untaxed * tax_multiplier
            foreign_currency_taxed = foreign_currency_untaxed * tax_multiplier

            buschluessel = ''

            # Standardmäßig gehen wir von einem Nettoexport aus
            csv_umsatz = foreign_currency_untaxed
            csv_basisbetrag = base_currency_untaxed
            csv_exchange_rate = exchange_rate
            if exchange_rate:
                # Maximal 4 Nachkommastellen in der CSV.
                # Bei der tatsächlichen Umrechnung nutzen wir alle.
                csv_exchange_rate = round(exchange_rate, 4)

            if export_method == 'gross':
                # Kunde wünscht export mit Bruttoangaben
                is_tax_archived = False
                if line.tax_line_id:
                    # Archivierte Steuerzeilen beachten
                    if line.tax_line_id.active is False:
                        is_tax_archived = True
                if (
                    line.account_id.is_tax_account()
                    and not (tax_exigibility and line.journal_id == cash_basis)
                    and not line.datev_posting_key == 'SD'
                    and len(move.line_ids) != 2
                    and not is_tax_archived
                ):
                    # ??? Bitte gewünschtes Verhalten dokumentieren!
                    # Wieso wird line.display_type == 'tax' nicht beachtet?
                    # Wieso wird line.tax_repartition_line_id nicht beachtet?
                    move_tax_lines += 1
                    continue

                if line.datev_posting_key == '40':
                    buschluessel = '40'
                    continue

                # Wechsle von Nettobeträgen zu Bruttobeträgen
                csv_umsatz = foreign_currency_taxed
                csv_basisbetrag = round(base_currency_taxed, 4)

                if not line.account_id.datev_automatic_account and tax:
                    # ??? Bitte gewünschtes Verhalten dokumentieren!
                    buschluessel = str(tax.l10n_de_datev_code)

            csv_umsatz = round(csv_umsatz, 2)
            csv_basisbetrag = round(csv_basisbetrag, 2)

            if csv_umsatz < 0:
                # Minusbeträge auf im export vermeiden
                csv_umsatz = -csv_umsatz
                csv_basisbetrag = -csv_basisbetrag

            if ignore_currency:
                # Kunde wünscht keine Angabe von Fremdwährungen
                # Basiswährungsangaben werden zur einzigen Währungsangabe
                csv_umsatz = csv_basisbetrag
                foreign_currency = base_currency
                base_currency = self.env['res.currency'].sudo()
                csv_basisbetrag = 0
                csv_exchange_rate = 0

            datevdict = {
                'Sollhaben': sollhaben,
                'Umsatz': str(csv_umsatz),
                'Waehrung': foreign_currency.name,
                'Kurs': str(csv_exchange_rate or '').replace('.', ','),
                'Basiswaehrungsbetrag': str(csv_basisbetrag or '').replace('.', ','),
                'Basiswaehrungskennung': base_currency.name or '',
                'Gegenkonto': datevgegenkonto,
                'Konto': datevkonto or '',
                'Buschluessel': buschluessel,
                'Movename': move.name,
                'Auftragsnummer': move.invoice_origin or '',
                'Festschreibung': str(int(bool(
                    move.restrict_mode_hash_table and move.inalterable_hash
                ))),
            }

            (
                errorcount,
                partnererror,
                thislog,
                thismovename,
                datevdict
            ) = self.field_config(
                move,
                line,
                errorcount,
                partnererror,
                thislog,
                thismovename,
                faelligkeit,
                datevdict,
            )

            datevdict = self._get_datev_dict(**datevdict)

            # ! TODO grouping does not work properly.
            # ! grouping adds 2*len(lines) lines with the
            # total of the move (2* = s+h each)
            if (
                self.env.user.company_id.datev_group_lines
                and move.journal_id.type not in ['bank', 'cash']
            ):
                if self.env.user.company_id.datev_group_sh:
                    self._datev_grouping_combined(
                        grouped_line,
                        line,
                        sollhaben,
                        csv_umsatz,
                        datevdict,
                    )
                else:
                    self._datev_grouping(
                        grouped_line,
                        line,
                        sollhaben,
                        csv_umsatz,
                        datevdict,
                    )
            else:
                grouped_line[line.id] = datevdict

            buchungszeilencount += 1
        bookingdict['move_bookings'] = [
            self._create_export_line(datevdict, rounding_method)
            for datevdict in grouped_line.values()
        ]
        return (
            buchungserror,
            errorcount,
            thislog,
            partnererror,
            buchungszeilencount,
            bookingdict,
            move_tax_lines
        )

    def _prepare_move(self, move, export_method):
        """
        Return the prepared move.

        :param move: account.move to prepare
        """
        if export_method == 'gross':
            move = self._match_journal_items(move)
        return move

    def _match_journal_items(self, move):
        """
        Match journal items.

        Matches the journal items and set the ref to the corresponding
        invoice number or ref.
        :param move: account.move

        :return account.move with matched lines
        """
        if not move.journal_id or move.journal_id.type not in ['bank']:
            return move

        recon_action = move.open_reconcile_view()

        # get all non invoice lines
        other_lines = self.env['account.move.line'].search(
            recon_action['domain']
        ).filtered(
            lambda r: r.journal_id.type not in ['sale', 'purchase']
        )

        # get all invoice lines
        for line in move.invoice_line_ids:
            ref = (
                line.move_id.name
                if line.ref and line.move_id.name in line.ref
                else line.ref or line.move_id.name
            )
            other_lines.filtered(
                lambda r: r.full_reconcile_id == line.full_reconcile_id
            ).write({
                'ref': ref,
            })
        return move

    def _datev_grouping(self, grouped, line, s_h, turnover, datev_dict):
        key = '{account_id}:{tax_id}:{s_h}:{kost1}:{kost2}'.format(
            account_id=line.account_id.id,
            tax_id=line.ecofi_tax_id.id,
            s_h=s_h,
            kost1=datev_dict['Kost1'],
            kost2=datev_dict['Kost2'],
        )

        if key not in grouped:
            grouped[key] = datev_dict
            return

        grp_turnover = Decimal(grouped[key]['Umsatz'].replace(',', '.'))
        new_turnover = Decimal(str(turnover).replace(',', '.'))
        grp_turnover += new_turnover

        grouped[key]['Umsatz'], _ = self.format_umsatz(
            Decimal(str(grp_turnover)),
        )

        if isinstance(line.name, str) and line.name != '/' and grouped.get(key, {}).get('Buchungstext'):
            line_name = (
                line.name
                    .replace('<p>', '')
                    .replace('</p>', '')
                    .replace('<br/>', '')
                    .replace('<br>', '')
                    .replace('[', '(')
                    .replace(']', ')')
                    .replace('\t', ' ')
            )
            grouped[key]['Buchungstext'] = '{bu_text}, {nbu_text}'.format(
                bu_text=grouped[key]['Buchungstext'],
                nbu_text=line_name,
            )

    def _datev_grouping_combined(
        self,
        grouped,
        line,
        s_h,
        turnover,
        datev_dict
    ):
        key = '{account_id}:{tax_id}:{kost1}:{kost2}'.format(
            account_id=line.account_id.id,
            tax_id=line.ecofi_tax_id.id,
            kost1=datev_dict['Kost1'],
            kost2=datev_dict['Kost2'],
        )

        if key not in grouped:
            grouped[key] = datev_dict
            return

        grp_turnover = Decimal(grouped[key]['Umsatz'].replace(',', '.'))
        new_turnover = Decimal(str(turnover).replace(',', '.'))

        if grouped[key]['Sollhaben'] != s_h:
            new_turnover = -new_turnover

        grp_turnover += new_turnover

        if grp_turnover < 0.0:
            grouped[key]['Sollhaben'] = (
                's'
                if grouped[key]['Sollhaben'] == 'h' else
                'h'
            )

        grouped[key]['Umsatz'], _ = self.format_umsatz(
            Decimal(str(grp_turnover)),
        )

        if isinstance(line.name, str) and line.name != '/' and grouped.get(key, {}).get('Buchungstext'):
            line_name = (
                line.name
                    .replace('<p>', '')
                    .replace('</p>', '')
                    .replace('<br/>', '')
                    .replace('<br>', '')
                    .replace('[', '(')
                    .replace(']', ')')
                    .replace('\t', ' ')
            )
            grouped[key]['Buchungstext'] = '{bu_text}, {nbu_text}'.format(
                bu_text=grouped[key]['Buchungstext'],
                nbu_text=line_name,
            )

    @staticmethod
    def _get_datev_dict(**kwargs) -> dict:
        return {
            'Sollhaben': kwargs.get('Sollhaben', ''),
            'Umsatz': kwargs.get('Umsatz', ''),
            'Gegenkonto': kwargs.get('Gegenkonto', ''),
            'Belegdatum': kwargs.get('Belegdatum', ''),
            'Konto': kwargs.get('Konto', ''),
            'Beleg1': kwargs.get('Beleg1', ''),
            'Beleg2': kwargs.get('Beleg2', ''),
            'Waehrung': kwargs.get('Waehrung', ''),
            'Buschluessel': kwargs.get('Buschluessel', ''),
            'Kost1': kwargs.get('Kost1', ''),
            'Kost2': kwargs.get('Kost2', ''),
            'Kostmenge': kwargs.get('Kostmenge', ''),
            'Skonto': kwargs.get('Skonto', ''),
            'Buchungstext': kwargs.get('Buchungstext', ''),
            'Beleglink': kwargs.get('Beleglink', ''),
            'BelegInfoArt1': kwargs.get('BelegInfoArt1', ''),
            'BelegInfoInhalt1': kwargs.get('BelegInfoInhalt1', ''),
            'EulandUSTID': kwargs.get('EulandUSTID', ''),
            'EUSteuer': kwargs.get('EUSteuer', ''),
            'Basiswaehrungsbetrag': kwargs.get('Basiswaehrungsbetrag', ''),
            'Basiswaehrungskennung': kwargs.get('Basiswaehrungskennung', ''),
            'Kurs': kwargs.get('Kurs', ''),
            'Movename': kwargs.get('Movename', ''),
            'Auftragsnummer': kwargs.get('Auftragsnummer', ''),
            'ZusatzInhalt1': kwargs.get('ZusatzInhalt1', ''),
            'Zusatzinformation - Art 1': kwargs.get('Zusatzinformation - Art 1', ''),
            'Festschreibung': kwargs.get('Festschreibung', ''),
            'Steuerperiode': kwargs.get('Steuerperiode', ''),
            'Leistungsdatum': kwargs.get('Leistungsdatum', ''),
        }

    @api.model
    def _create_export_line(self, datev_dict: dict, rounding_method):
        """
        Create the datev csv move line.
        """
        return self.env['ecofi.export.columns'].get_datev_export_line(
            self._normalize_datev_dict(datev_dict, rounding_method),
        )

    def _normalize_datev_dict(self, datev_dict: dict, rounding_method) -> dict:
        normalized_dict = dict(datev_dict)

        if normalized_dict.get('Buschluessel') == '0':
            normalized_dict['Buschluessel'] = ''

        normalized_dict['Sollhaben'] = normalized_dict['Sollhaben'].upper()

        if normalized_dict.get('Buchungstext'):
            normalized_dict['Buchungstext'] = '{:.55}'.format(
                normalized_dict['Buchungstext'],
            )

        if normalized_dict.get('Beleg1'):
            beleg1 = normalized_dict['Beleg1']

            normalized_dict['Beleg1'] = '{}'.format(
                re.sub(
                    r'[^0-9A-Za-z$&%*+\-/]',
                    '',
                    beleg1,
                ).replace('.', ''),
            )[-36:]

        if normalized_dict.get('Beleg2'):
            normalized_dict['Beleg2'] = '{}'.format(
                re.sub(
                    '[^{}]'.format(Ecofi._get_valid_chars()),
                    '',
                    normalized_dict['Beleg2'],
                ).replace('.', ''),
            )[-36:]

        if normalized_dict.get('Umsatz'):
            if rounding_method == 'round_globally':
                normalized_dict['Umsatz'] = str(
                    round(Decimal(str(
                        normalized_dict['Umsatz'].replace(',', '.')
                    )), 2)
                ).replace('.', ',')
            elif rounding_method == 'round_per_line':
                normalized_dict['Umsatz'] = str(normalized_dict['Umsatz']).replace('.', ',')

        return normalized_dict

    def ecofi_buchungen(self, journal_ids, date_from, date_to):
        return super(Ecofi, self.with_context(
            datev_ignore_currency=self.env.company.datev_ignore_currency,
        )).ecofi_buchungen(journal_ids, date_from, date_to)

    @staticmethod
    def _get_valid_chars(additional_chars=None):
        """
        Get valid chars for Belegfeld 1 and Belegfeld 2.

        Those can be used e.g. in a RegEx.

        :param str additional_chars:
        :return: a string containing valid chars
        :rtype: str
        """
        chars = r'a-zA-Z0-9$%&*+\-/'

        if additional_chars and isinstance(additional_chars, str):
            chars += additional_chars

        return chars
