# Developed by ecoservice (Uwe Böttcher und Falk Neubert GbR).
# See COPYRIGHT and LICENSE files in the root directory of this module for full details.

from . import core


class Description30(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        value = str(value)
        return (
            value[0:30]
            if value and len(value) > 30 else
            value
        )


class Description40(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        value = str(value)
        return (
            value[0:40]
            if value and len(value) > 40 else
            value
        )


class Description50(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        value = str(value)
        return (
            value[0:50]
            if value and len(value) > 50 else
            value
        )


class Description255(core.XsdSimpleType):

    def __new__(
        cls,
        value,
    ) -> str:
        if not value:
            return None

        value = str(value)
        return (
            value[0:255]
            if value and len(value) > 255 else
            value
        )
