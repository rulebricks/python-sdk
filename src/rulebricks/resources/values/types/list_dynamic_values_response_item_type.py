# This file was auto-generated by Fern from our API Definition.

import enum
import typing

T_Result = typing.TypeVar("T_Result")


class ListDynamicValuesResponseItemType(str, enum.Enum):
    """
    Data type of the dynamic value.
    """

    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    LIST = "list"

    def visit(
        self,
        string: typing.Callable[[], T_Result],
        number: typing.Callable[[], T_Result],
        boolean: typing.Callable[[], T_Result],
        list_: typing.Callable[[], T_Result],
    ) -> T_Result:
        if self is ListDynamicValuesResponseItemType.STRING:
            return string()
        if self is ListDynamicValuesResponseItemType.NUMBER:
            return number()
        if self is ListDynamicValuesResponseItemType.BOOLEAN:
            return boolean()
        if self is ListDynamicValuesResponseItemType.LIST:
            return list_()
