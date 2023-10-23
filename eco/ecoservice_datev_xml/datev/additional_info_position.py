# <xsd:element name="additional_info_position">
#     <xsd:complexType>
#         <xsd:annotation>
#             <xsd:documentation>
#               xsd:attribute type: additional field for unavailable information content:
#               the attribute Type contains the missing attribute names (structuring names)
#             </xsd:documentation>
#             <xsd:documentation>
#               xsd:attribute content: additional field for unavailable information content:
#               the attribute Content describes the missing attributes; it contains the value.
#             </xsd:documentation>
#         </xsd:annotation>
#         <xsd:attribute name="type" type="de:p10008" use="required"/>
#         <xsd:attribute name="content" type="de:p10016" use="required"/>
#     </xsd:complexType>
# </xsd:element>
