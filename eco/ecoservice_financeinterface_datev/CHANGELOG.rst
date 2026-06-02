Changelog
=========

16.0.2.6.7
----------
* 114797: move.name for Beleg1 in outgoing invoices

16.0.2.6.6
----------
* 114195: include tax lines in export not created from other move lines

16.0.2.6.5
----------
* 113633: Comma instead of point for decimal places at exchange rates

16.0.2.6.4
----------
* 113578: fix zero export traceback

16.0.2.6.3
----------
* 113225: revert point in comma logic for kurs

16.0.2.6.2
----------
* 113192: revert part of Belegfeld logic

16.0.2.6.1
----------
* 113173: Optionally show account counterpart field

16.0.2.6.0
----------
* [FIX] 113150: Point in comma value exports
* [FIX] "Umsatz" vs. "Basiswährungsumsatz" mismatch
* [IMP] Code cleanup

16.0.2.5.9
----------
* 113073: Allow the export of zero values


16.0.2.5.8
----------
* 112843, 112906 - [FIX] AttributeError: 'account.payment' object has no attribute '_get_outstanding_account'

16.0.2.5.7
----------
* Fix Type-Annotation

16.0.2.5.3
----------
* 112667 - backport changes from version 18 (#112346 get amount total by datev group lines.)

16.0.1.0.0
----------
* Migration to 16.0

15.0.1.6.1
----------
* Fix wrong counter account in some cases

15.0.1.6.0
----------
* Prevent error with exchange moves

15.0.1.5.0
----------
* Add: Document link type in config and export

15.0.1.4.0
----------
* Add: Beleglink in export

15.0.1.3.1
----------
* Fix: migrate moves

15.0.1.3.0
----------
* Add: delivery date in invoice and export

15.0.1.2.0
----------
* Added system parameter to change tax amount
* Add: date in Steuerperiode
* Fix missing EulandUSTID Error

15.0.1.1.0
----------
* Add Odoo Bill no to Export

15.0.1.0.1
----------
* Fix: Remove dots from Belegfeld

15.0.1.0.0
----------
* Migration to 15.0

14.0.1.7.1
----------
* Fix missing EulandUSTID Error

14.0.1.7.0
----------
* Fix cent differences
* Fix invoice in Belegfeld 1
* Fix counteraccount on invoice after editing a inovice line

14.0.1.6.2
----------
* Possible FIX differences on datev export

14.0.1.6.1
----------
* FIX EU Tax in Datev Export - Replace dot by comma

14.0.1.6.0
----------
* Name of Partner in DATEV-Export (Zusatzinformation- Inhalt 1)

14.0.1.5.0
----------
* EU Tax in Datev Export

14.0.1.4.4
----------
* Prevent multiple currency rates failure

14.0.1.4.3
----------
* Fix differences in currency

14.0.1.4.2
----------
* Fix: missing counterpart on reconcile

14.0.1.4.1
----------
* Bugfix for not setting counter account correctly in some cases

14.0.1.4.0
----------
* Optimize and refactor logic for setting counter account

14.0.1.3.1
----------
* Extend Belegfeld to 36 Chars

14.0.1.3.0
----------
* Include order number in export

14.0.1.2.0
----------
* Include past currency exchange rates in multicurrency exports

14.0.1.1.1
----------
* Migration to 14.0

13.0.1.1.1
----------
* Fix prevention of invoices being posted if it contains a comment line

13.0.1.1.0
----------
* Updated Datev Data

13.0.1.0.2
----------
* Fix wrong date format in export

13.0.1.0.1
----------
* Fix IndexError during migration if assigned taxes are archived

13.0.1.0.0
----------
* Migration to 13.0
