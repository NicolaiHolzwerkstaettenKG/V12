Changelog
=========
16.0.1.2.0
----------
* Added Field in journal so the bank account data is only shown on invoice if set to true

16.0.1.1.0
----------
* add fields footer_as_image and footer_image in the base_document_layout.
* print the footer as image if the iamge available and the footer_image is true.

16.0.1.0.3
----------
* Fix Bank journal printing on reports

16.0.1.0.2
----------
* Customizing table.

16.0.1.0.1
----------
* Layout Customizing.

16.0.1.0.0
----------
* Migration to V16.

15.0.1.1.0
----------
* User can selected in the German Document config, which language is standard for the Print Document.

15.0.1.0.1
----------
* Fixed a bug where the PDFs where not saved as attachments when printing via mass print

15.0.1.0.0
----------
* Migrated from Version 14.0
* add the field "amount_by_group" and the Methode "_amount_by_group"

14.0.1.2.3
----------
* Fix customer-reference

14.0.1.2.2
----------
* Fix 14.0 specific bug in the layout preview wizard
* Fix 14.0 specific bug in safe_eval

14.0.1.2.1
----------
* Support for OCA module partner fax

14.0.1.2.0
----------
* Migrated from Version 13.0

13.0.1.2.0
----------
* Font-Family for reports now depends on company settings

13.0.1.1.0
----------
* Print country name in address according to DIN 5008

13.0.1.0.4
----------
* Fixed AttributeError when accessing settings

13.0.1.0.3
----------
* Fixed KeyError caused by missing company_id in relation to report_table_position
* Fixed CacheMiss error for mixin field

13.0.1.0.2
----------
* Fixed if-statement orders for Unit Testing

13.0.1.0.1
----------
* Added possibility to hide payments

13.0.1.0.0
----------
* Migrated from Version 12.0
