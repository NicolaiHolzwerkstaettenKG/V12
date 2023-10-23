# <xsd:element name="discount">
#     <xsd:complexType>
#         <xsd:annotation>
#             <xsd:documentation>
#               xsd:attribute payment_date: Date by which discount percentages apply
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute discount_percentage: percentage discount to deduct,
#               figure given always includes decimal places
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute discount_base_amount: Amount from which the discount deduction is calculated,
#               figure given always includes decimal places
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute discount_tax: Tax rate applicable to discount amount,
#               figure given always includes decimal places
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute discount_tax_amount: Amount of tax on discount,
#               figure given always includes decimal places
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute discount_amount: discount amount, figure given always includes decimal places
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute currency: Currency code for the above amounts
#             </xsd:documentation>
#         </xsd:annotation>
#         <xsd:attribute name="payment_date" type="de:p10029" use="optional"/>
#         <xsd:attribute name="discount_percentage" type="de:p10020" use="optional"/>
#         <xsd:attribute name="discount_base_amount" type="de:p7" use="optional"/>
#         <xsd:attribute name="discount_tax" type="de:p10020" use="required"/>
#         <xsd:attribute name="discount_tax_amount" type="de:p7" use="optional"/>
#         <xsd:attribute name="discount_amount" type="de:p12" use="optional"/>
#         <xsd:attribute name="currency" type="de:p1" use="optional"/>
#     </xsd:complexType>
# </xsd:element>
