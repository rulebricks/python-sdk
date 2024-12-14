from typing import Any, Union, List, Optional, Generic, TypeVar
from datetime import datetime
from .types import OperatorDef, OperatorArg, Field, DynamicValueType, TypeMismatchError
from .values import DynamicValue

T = TypeVar('T')
U = TypeVar('U')  # For handling nested generic types

class Argument(Generic[T]):
    """Represents a value that could be either a primitive or dynamic value"""
    def __init__(self, value: Union[T, DynamicValue], expected_type: DynamicValueType):
        self.value = value
        self.expected_type = expected_type
        self._validate_type()

    def _validate_type(self) -> None:
        """Validate that the value matches the expected type"""
        if isinstance(self.value, DynamicValue):
            if self.value.value_type != self.expected_type:
                raise TypeMismatchError(
                    f"Dynamic value '{self.value.name}' has type {self.value.value_type.value}, "
                    f"but {self.expected_type.value} was expected"
                )
        else:
            expected_python_type = DynamicValue.get_expected_type(self.expected_type)
            if not isinstance(self.value, expected_python_type):
                actual_type = type(self.value).__name__
                raise TypeMismatchError(
                    f"Value {self.value} has type {actual_type}, "
                    f"but {self.expected_type.value} was expected"
                )

    def to_dict(self) -> Any:
        if isinstance(self.value, DynamicValue):
            return self.value.to_dict()
        return self.value

    @classmethod
    def process(cls, arg: Any, expected_type: DynamicValueType) -> Any:
        """Process any argument into the correct format for conditions"""
        if isinstance(arg, Argument):
            return arg.to_dict()
        elif isinstance(arg, DynamicValue):
            return arg.to_dict()
        elif isinstance(arg, list):
            return [cls.process(item, expected_type) for item in arg]
        elif isinstance(arg, dict):
            return {k: cls.process(v, expected_type) for k, v in arg.items()}
        return arg

    def __repr__(self) -> str:
        if isinstance(self.value, DynamicValue):
            return f"<{self.value.name.upper()}>"
        return f"{self.value}"


class BooleanField(Field):
    """Valid boolean comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: bool = False):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef("any", [], "Match any boolean value", skip_typecheck=True),
            "is_true": OperatorDef("is true", [], "Check if value is true"),
            "is_false": OperatorDef("is false", [], "Check if value is false")
        }

    def equals(self, value: Union[bool, DynamicValue]) -> tuple:
        """Check if value equals the given boolean"""
        arg = Argument(value, DynamicValueType.BOOLEAN)
        op_name = "is true" if value else "is false"
        return (op_name, [arg])

    def any(self) -> tuple:
        """Match any boolean value"""
        return ("any", [])

class NumberField(Field):
    """Valid number comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: Union[int, float] = 0):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef("any", [], "Match any numeric value", skip_typecheck=True),
            "equals": OperatorDef("equals", [OperatorArg("value", "number", "Number that value must equal")]),
            "does_not_equal": OperatorDef("does not equal", [OperatorArg("value", "number", "Number that value must not equal")]),
            "greater_than": OperatorDef("greater than", [OperatorArg("bound", "number", "Number that value must be greater than")]),
            "less_than": OperatorDef("less than", [OperatorArg("bound", "number", "Number that value must be less than")]),
            "greater_than_or_equal": OperatorDef("greater than or equal to", [OperatorArg("bound", "number", "Number that value must be greater than or equal to")]),
            "less_than_or_equal": OperatorDef("less than or equal to", [OperatorArg("bound", "number", "Number that value must be less than or equal to")]),
            "between": OperatorDef(
                "between",
                [
                    OperatorArg("start", "number", "Number that value must be greater than or equal to", placeholder="Start"),
                    OperatorArg("end", "number", "Number that value must be less than or equal to", placeholder="End")
                ],
                validate=lambda args: args[0] < args[1]
            ),
            "not_between": OperatorDef(
                "not between",
                [
                    OperatorArg("start", "number", "Number that value must be less than", placeholder="Start"),
                    OperatorArg("end", "number", "Number that value must be greater than", placeholder="End")
                ],
                validate=lambda args: args[0] < args[1]
            ),
            "is_even": OperatorDef("is even", [], "Check if value is even"),
            "is_odd": OperatorDef("is odd", [], "Check if value is odd"),
            "is_positive": OperatorDef("is positive", [], "Check if value is greater than zero"),
            "is_negative": OperatorDef("is negative", [], "Check if value is less than zero"),
            "is_zero": OperatorDef("is zero", [], "Check if value equals zero"),
            "is_not_zero": OperatorDef("is not zero", [], "Check if value does not equal zero"),
            "is_multiple_of": OperatorDef("is a multiple of", [OperatorArg("multiple", "number", "Number that value must be a multiple of")]),
            "is_not_multiple_of": OperatorDef("is not a multiple of", [OperatorArg("multiple", "number", "Number that value must not be a multiple of")]),
            "is_power_of": OperatorDef(
                "is a power of",
                [OperatorArg("base", "number", "The base number")],
                validate=lambda args: args[0] > 0
            )
        }

    def equals(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("equals", [Argument(value, DynamicValueType.NUMBER)])

    def not_equals(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("does not equal", [Argument(value, DynamicValueType.NUMBER)])

    def greater_than(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("greater than", [Argument(value, DynamicValueType.NUMBER)])

    def less_than(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("less than", [Argument(value, DynamicValueType.NUMBER)])

    def greater_than_or_equal(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("greater than or equal to", [Argument(value, DynamicValueType.NUMBER)])

    def less_than_or_equal(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("less than or equal to", [Argument(value, DynamicValueType.NUMBER)])

    def between(self, start: Union[int, float, DynamicValue], end: Union[int, float, DynamicValue]) -> tuple:
        start_arg = Argument(start, DynamicValueType.NUMBER)
        end_arg = Argument(end, DynamicValueType.NUMBER)
        if not isinstance(start, DynamicValue) and not isinstance(end, DynamicValue):
            op = self.operators["between"]
            if op.validate and not op.validate([start, end]):
                raise ValueError(f"Invalid range for between: start ({start}) must be less than end ({end})")
        return ("between", [start_arg, end_arg])

    def not_between(self, start: Union[int, float, DynamicValue], end: Union[int, float, DynamicValue]) -> tuple:
        start_arg = Argument(start, DynamicValueType.NUMBER)
        end_arg = Argument(end, DynamicValueType.NUMBER)
        if not isinstance(start, DynamicValue) and not isinstance(end, DynamicValue):
            op = self.operators["not_between"]
            if op.validate and not op.validate([start, end]):
                raise ValueError(f"Invalid range for not between: start ({start}) must be less than end ({end})")
        return ("not between", [start_arg, end_arg])

    def is_even(self) -> tuple:
        return ("is even", [])

    def is_odd(self) -> tuple:
        return ("is odd", [])

    def is_positive(self) -> tuple:
        return ("is positive", [])

    def is_negative(self) -> tuple:
        return ("is negative", [])

    def is_zero(self) -> tuple:
        return ("is zero", [])

    def is_not_zero(self) -> tuple:
        return ("is not zero", [])

    def is_multiple_of(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("is a multiple of", [Argument(value, DynamicValueType.NUMBER)])

    def is_not_multiple_of(self, value: Union[int, float, DynamicValue]) -> tuple:
        return ("is not a multiple of", [Argument(value, DynamicValueType.NUMBER)])

    def is_power_of(self, base: Union[int, float, DynamicValue]) -> tuple:
        if not isinstance(base, DynamicValue):
            op = self.operators["is_power_of"]
            if op.validate and not op.validate([base]):
                raise ValueError(f"Invalid base for is power of: {base}. Base must be positive.")
        return ("is a power of", [Argument(base, DynamicValueType.NUMBER)])

class StringField(Field):
    """Valid text comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: str = ""):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef("any", [], "Match any string value", skip_typecheck=True),
            "contains": OperatorDef(
                "contains",
                [OperatorArg("value", "string", "The value to search for within the string", validate=lambda x: len(x) > 0)]
            ),
            "does_not_contain": OperatorDef(
                "does not contain",
                [OperatorArg("value", "string", "The value to search for within the string", validate=lambda x: len(x) > 0)]
            ),
            "equals": OperatorDef("equals", [OperatorArg("value", "string", "The value to compare against")]),
            "does_not_equal": OperatorDef("does not equal", [OperatorArg("value", "string", "The value to compare against")]),
            "is_empty": OperatorDef("is empty", [], "Check if string is empty"),
            "is_not_empty": OperatorDef("is not empty", [], "Check if string is not empty"),
            "starts_with": OperatorDef(
                "starts with",
                [OperatorArg("value", "string", "The value the string should start with", validate=lambda v: len(v) > 0)]
            ),
            "ends_with": OperatorDef(
                "ends with",
                [OperatorArg("value", "string", "The value the string should end with", validate=lambda v: len(v) > 0)]
            ),
            "is_included_in": OperatorDef(
                "is included in",
                [OperatorArg("value", "list", "A list of values the string should be in", validate=lambda v: len(v) > 0)]
            ),
            "is_not_included_in": OperatorDef(
                "is not included in",
                [OperatorArg("value", "list", "A list of values the string should not be in", validate=lambda v: len(v) > 0)]
            ),
            "matches_regex": OperatorDef(
                "matches RegEx",
                [OperatorArg("regex", "string", "The regex the string should match", validate=lambda v: len(v) > 0)]
            ),
            "does_not_match_regex": OperatorDef(
                "does not match RegEx",
                [OperatorArg("regex", "string", "The regex the string should not match", validate=lambda v: len(v) > 0)]
            ),
            "is_valid_email": OperatorDef("is a valid email address", [], "Check if string is a valid email address"),
            "is_not_valid_email": OperatorDef("is not a valid email address", [], "Check if string is not a valid email address"),
            "is_valid_url": OperatorDef("is a valid URL", [], "Check if string is a valid URL"),
            "is_not_valid_url": OperatorDef("is not a valid URL", [], "Check if string is not a valid URL"),
            "is_valid_ip": OperatorDef("is a valid IP address", [], "Check if string is a valid IP address"),
            "is_not_valid_ip": OperatorDef("is not a valid IP address", [], "Check if string is not a valid IP address"),
            "is_uppercase": OperatorDef("is uppercase", [], "Check if string is all uppercase"),
            "is_lowercase": OperatorDef("is lowercase", [], "Check if string is all lowercase"),
            "is_numeric": OperatorDef("is numeric", [], "Check if string contains only numeric characters"),
            "contains_only_digits": OperatorDef("contains only digits", [], "Check if string contains only digits"),
            "contains_only_letters": OperatorDef("contains only letters", [], "Check if string contains only letters"),
            "contains_only_digits_and_letters": OperatorDef(
                "contains only digits and letters",
                [],
                "Check if string contains only digits and letters"
            )
        }

    def contains(self, value: Union[str, DynamicValue]) -> tuple:
        arg = Argument(value, DynamicValueType.STRING)
        if not isinstance(value, DynamicValue):
            op = self.operators["contains"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for contains: {value}")
        return ("contains", [arg])

    def not_contains(self, value: Union[str, DynamicValue]) -> tuple:
        arg = Argument(value, DynamicValueType.STRING)
        if not isinstance(value, DynamicValue):
            op = self.operators["does_not_contain"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for does not contain: {value}")
        return ("does not contain", [arg])

    def equals(self, value: Union[str, DynamicValue]) -> tuple:
        return ("equals", [Argument(value, DynamicValueType.STRING)])

    def not_equals(self, value: Union[str, DynamicValue]) -> tuple:
        return ("does not equal", [Argument(value, DynamicValueType.STRING)])

    def is_empty(self) -> tuple:
        return ("is empty", [])

    def is_not_empty(self) -> tuple:
        return ("is not empty", [])

    def starts_with(self, value: Union[str, DynamicValue]) -> tuple:
        arg = Argument(value, DynamicValueType.STRING)
        if not isinstance(value, DynamicValue):
            op = self.operators["starts_with"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for starts with: {value}")
        return ("starts with", [arg])

    def ends_with(self, value: Union[str, DynamicValue]) -> tuple:
        arg = Argument(value, DynamicValueType.STRING)
        if not isinstance(value, DynamicValue):
            op = self.operators["ends_with"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for ends with: {value}")
        return ("ends with", [arg])

    def is_included_in(self, values: Union[List[str], List[DynamicValue], DynamicValue]) -> tuple:
        if isinstance(values, DynamicValue):
            if values.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(
                    f"Dynamic value '{values.name}' has type {values.value_type.value}, "
                    f"but list was expected"
                )
            return ("is included in", [Argument(values, DynamicValueType.LIST)])

        op = self.operators["is_included_in"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")

        return ("is included in", [[Argument(v, DynamicValueType.STRING) for v in values]])

    def matches_regex(self, pattern: Union[str, DynamicValue]) -> tuple:
        arg = Argument(pattern, DynamicValueType.STRING)
        if not isinstance(pattern, DynamicValue):
            op = self.operators["matches_regex"]
            if op.args[0].validate and not op.args[0].validate(pattern):
                raise ValueError(f"Invalid regex pattern: {pattern}")
        return ("matches RegEx", [arg])

    def not_matches_regex(self, pattern: Union[str, DynamicValue]) -> tuple:
        arg = Argument(pattern, DynamicValueType.STRING)
        if not isinstance(pattern, DynamicValue):
            op = self.operators["does_not_match_regex"]
            if op.args[0].validate and not op.args[0].validate(pattern):
                raise ValueError(f"Invalid regex pattern: {pattern}")
        return ("does not match RegEx", [arg])

    def is_email(self) -> tuple:
        return ("is a valid email address", [])

    def is_not_email(self) -> tuple:
        return ("is not a valid email address", [])

    def is_url(self) -> tuple:
        return ("is a valid URL", [])

    def is_not_url(self) -> tuple:
        return ("is not a valid URL", [])

    def is_ip(self) -> tuple:
        return ("is a valid IP address", [])

    def is_not_ip(self) -> tuple:
        return ("is not a valid IP address", [])

    def is_uppercase(self) -> tuple:
        return ("is uppercase", [])

    def is_lowercase(self) -> tuple:
        return ("is lowercase", [])

    def is_numeric(self) -> tuple:
        return ("is numeric", [])

    def contains_only_digits(self) -> tuple:
        return ("contains only digits", [])

    def contains_only_letters(self) -> tuple:
        return ("contains only letters", [])

    def contains_only_digits_and_letters(self) -> tuple:
        return ("contains only digits and letters", [])

class DateField(Field):
    """Valid date comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: Optional[datetime] = None):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef("any", [], "Match any date value", skip_typecheck=True),
            "is_past": OperatorDef("is in the past", [], "Date is in the past"),
            "is_future": OperatorDef("is in the future", [], "Date is in the future"),
            "days_ago": OperatorDef(
                "days ago",
                [OperatorArg("days", "number", "Number of days ago that the date is equal to")]
            ),
            "less_than_days_ago": OperatorDef(
                "is less than N days ago",
                [OperatorArg("days", "number", "Number of days ago that the date is less than or equal to")]
            ),
            "more_than_days_ago": OperatorDef(
                "is more than N days ago",
                [OperatorArg("days", "number", "Number of days ago that the date is more than or equal to")]
            ),
            "days_from_now": OperatorDef(
                "days from now",
                [OperatorArg("days", "number", "Number of days from now that the date is equal to")]
            ),
            "less_than_days_from_now": OperatorDef(
                "is less than N days from now",
                [OperatorArg("days", "number", "Number of days from now that the date is less than or equal to")]
            ),
            "more_than_days_from_now": OperatorDef(
                "is more than N days from now",
                [OperatorArg("days", "number", "Number of days from now that the date is more than or equal to")]
            ),
            "is_today": OperatorDef("is today", [], "Date is today"),
            "is_this_week": OperatorDef("is this week", [], "Date is in the current week"),
            "is_this_month": OperatorDef("is this month", [], "Date is in the current month"),
            "is_this_year": OperatorDef("is this year", [], "Date is in the current year"),
            "is_next_week": OperatorDef("is next week", [], "Date is in the next week"),
            "is_next_month": OperatorDef("is next month", [], "Date is in the next month"),
            "is_next_year": OperatorDef("is next year", [], "Date is in the next year"),
            "is_last_week": OperatorDef("is last week", [], "Date is in the previous week"),
            "is_last_month": OperatorDef("is last month", [], "Date is in the previous month"),
            "is_last_year": OperatorDef("is last year", [], "Date is in the previous year"),
            "after": OperatorDef(
                "after",
                [OperatorArg("date", "date", "Date that value must be after")]
            ),
            "on_or_after": OperatorDef(
                "on or after",
                [OperatorArg("date", "date", "Date that value must be on or after")]
            ),
            "before": OperatorDef(
                "before",
                [OperatorArg("date", "date", "Date that value must be before")]
            ),
            "on_or_before": OperatorDef(
                "on or before",
                [OperatorArg("date", "date", "Date that value must be on or before")]
            ),
            "between": OperatorDef(
                "between",
                [
                    OperatorArg("start", "date", "Date that value must be after", placeholder="From"),
                    OperatorArg("end", "date", "Date that value must be before", placeholder="To")
                ]
            ),
            "not_between": OperatorDef(
                "not between",
                [
                    OperatorArg("start", "date", "Date that value must be before", placeholder="From"),
                    OperatorArg("end", "date", "Date that value must be after", placeholder="To")
                ]
            )
        }

    def is_past(self) -> tuple:
        return ("is in the past", [])

    def is_future(self) -> tuple:
        return ("is in the future", [])

    def days_ago(self, days: Union[int, DynamicValue]) -> tuple:
        return ("days ago", [Argument(days, DynamicValueType.NUMBER)])

    def less_than_days_ago(self, days: Union[int, DynamicValue]) -> tuple:
        return ("is less than N days ago", [Argument(days, DynamicValueType.NUMBER)])

    def more_than_days_ago(self, days: Union[int, DynamicValue]) -> tuple:
        return ("is more than N days ago", [Argument(days, DynamicValueType.NUMBER)])

    def days_from_now(self, days: Union[int, DynamicValue]) -> tuple:
        return ("days from now", [Argument(days, DynamicValueType.NUMBER)])

    def less_than_days_from_now(self, days: Union[int, DynamicValue]) -> tuple:
        return ("is less than N days from now", [Argument(days, DynamicValueType.NUMBER)])

    def more_than_days_from_now(self, days: Union[int, DynamicValue]) -> tuple:
        return ("is more than N days from now", [Argument(days, DynamicValueType.NUMBER)])

    def is_today(self) -> tuple:
        return ("is today", [])

    def is_this_week(self) -> tuple:
        return ("is this week", [])

    def is_this_month(self) -> tuple:
        return ("is this month", [])

    def is_this_year(self) -> tuple:
        return ("is this year", [])

    def is_next_week(self) -> tuple:
        return ("is next week", [])

    def is_next_month(self) -> tuple:
        return ("is next month", [])

    def is_next_year(self) -> tuple:
        return ("is next year", [])

    def is_last_week(self) -> tuple:
        return ("is last week", [])

    def is_last_month(self) -> tuple:
        return ("is last month", [])

    def is_last_year(self) -> tuple:
        return ("is last year", [])

    def after(self, date: Union[datetime, str, DynamicValue]) -> tuple:
        return ("after", [Argument(date, DynamicValueType.DATE)])

    def on_or_after(self, date: Union[datetime, str, DynamicValue]) -> tuple:
        return ("on or after", [Argument(date, DynamicValueType.DATE)])

    def before(self, date: Union[datetime, str, DynamicValue]) -> tuple:
        return ("before", [Argument(date, DynamicValueType.DATE)])

    def on_or_before(self, date: Union[datetime, str, DynamicValue]) -> tuple:
        return ("on or before", [Argument(date, DynamicValueType.DATE)])

    def between(self, start: Union[datetime, str, DynamicValue], end: Union[datetime, str, DynamicValue]) -> tuple:
        return ("between", [Argument(start, DynamicValueType.DATE), Argument(end, DynamicValueType.DATE)])

    def not_between(self, start: Union[datetime, str, DynamicValue], end: Union[datetime, str, DynamicValue]) -> tuple:
        return ("not between", [Argument(start, DynamicValueType.DATE), Argument(end, DynamicValueType.DATE)])

class ListField(Field):
    """Valid list comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: Optional[List] = None):
        super().__init__(name, description, default or [])
        self.operators = {
            "any": OperatorDef("any", [], "Match any list value", skip_typecheck=True),
            "contains": OperatorDef(
                "contains",
                [OperatorArg("value", "generic", "Value that must be contained in the list")]
            ),
            "is_empty": OperatorDef("is empty", [], "Check if list is empty"),
            "is_not_empty": OperatorDef("is not empty", [], "Check if list is not empty"),
            "is_of_length": OperatorDef(
                "is of length",
                [OperatorArg("length", "number", "Length that the list must be")]
            ),
            "is_not_of_length": OperatorDef(
                "is not of length",
                [OperatorArg("length", "number", "Length that the list must not be")]
            ),
            "is_longer_than": OperatorDef(
                "is longer than",
                [OperatorArg("length", "number", "Length that the list must be longer than")]
            ),
            "is_shorter_than": OperatorDef(
                "is shorter than",
                [OperatorArg("length", "number", "Length that the list must be shorter than")]
            ),
            "contains_all_of": OperatorDef(
                "contains all of",
                [OperatorArg("values", "list", "List of values that must be contained in the list")]
            ),
            "contains_any_of": OperatorDef(
                "contains any of",
                [OperatorArg("values", "list", "List of values that might be contained in the list")]
            ),
            "contains_none_of": OperatorDef(
                "contains none of",
                [OperatorArg("values", "list", "List of values that must not be contained in the list")]
            ),
            "does_not_contain": OperatorDef(
                "does not contain",
                [OperatorArg("value", "generic", "Value that must not be contained in the list")]
            ),
            "is_equal_to": OperatorDef(
                "is equal to",
                [OperatorArg("list", "list", "Value that the list must be equal to")]
            ),
            "is_not_equal_to": OperatorDef(
                "is not equal to",
                [OperatorArg("list", "list", "Value that the list must not be equal to")]
            ),
            "contains_duplicates": OperatorDef("contains duplicates", [], "Check if list contains duplicate values"),
            "does_not_contain_duplicates": OperatorDef("does not contain duplicates", [], "Check if list does not contain duplicate values"),
            "contains_object_with_key_value": OperatorDef(
                "contains object with key & value",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg("value", "generic", "Value that the key must be equal to")
                ]
            )
        }

    def contains(self, value: Union[Any, DynamicValue]) -> tuple:
        return ("contains", [Argument(value, DynamicValueType.OBJECT)])  # Use OBJECT type for generic values

    def is_empty(self) -> tuple:
        return ("is empty", [])

    def is_not_empty(self) -> tuple:
        return ("is not empty", [])

    def length_equals(self, length: Union[int, DynamicValue]) -> tuple:
        return ("is of length", [Argument(length, DynamicValueType.NUMBER)])

    def length_not_equals(self, length: Union[int, DynamicValue]) -> tuple:
        return ("is not of length", [Argument(length, DynamicValueType.NUMBER)])

    def longer_than(self, length: Union[int, DynamicValue]) -> tuple:
        return ("is longer than", [Argument(length, DynamicValueType.NUMBER)])

    def shorter_than(self, length: Union[int, DynamicValue]) -> tuple:
        return ("is shorter than", [Argument(length, DynamicValueType.NUMBER)])

    def contains_all(self, values: Union[List[Any], DynamicValue]) -> tuple:
        if isinstance(values, DynamicValue):
            if values.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains all of", [Argument(values, DynamicValueType.LIST)])
        return ("contains all of", [[Argument(v, DynamicValueType.OBJECT) for v in values]])

    def contains_any(self, values: Union[List[Any], DynamicValue]) -> tuple:
        if isinstance(values, DynamicValue):
            if values.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains any of", [Argument(values, DynamicValueType.LIST)])
        return ("contains any of", [[Argument(v, DynamicValueType.OBJECT) for v in values]])

    def contains_none(self, values: Union[List[Any], DynamicValue]) -> tuple:
        if isinstance(values, DynamicValue):
            if values.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains none of", [Argument(values, DynamicValueType.LIST)])
        return ("contains none of", [[Argument(v, DynamicValueType.OBJECT) for v in values]])

    def not_contains(self, value: Union[Any, DynamicValue]) -> tuple:
        """Check if list does not contain value"""
        return ("does not contain", [Argument(value, DynamicValueType.OBJECT)])

    def equals(self, other: Union[List[Any], DynamicValue]) -> tuple:
        """Check if list equals another list"""
        if isinstance(other, DynamicValue):
            if other.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{other.name}' has type {other.value_type.value}, but list was expected")
            return ("is equal to", [Argument(other, DynamicValueType.LIST)])
        return ("is equal to", [[Argument(v, DynamicValueType.OBJECT) for v in other]])

    def not_equals(self, other: Union[List[Any], DynamicValue]) -> tuple:
        """Check if list does not equal another list"""
        if isinstance(other, DynamicValue):
            if other.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{other.name}' has type {other.value_type.value}, but list was expected")
            return ("is not equal to", [Argument(other, DynamicValueType.LIST)])
        return ("is not equal to", [[Argument(v, DynamicValueType.OBJECT) for v in other]])

    def has_duplicates(self) -> tuple:
        """Check if list has duplicate values"""
        return ("contains duplicates", [])

    def no_duplicates(self) -> tuple:
        """Check if list has no duplicate values"""
        return ("does not contain duplicates", [])

    def contains_object_with_key_value(self, key: Union[str, DynamicValue], value: Union[Any, DynamicValue]) -> tuple:
        """Check if list contains an object with specified key and value"""
        return ("contains object with key & value", [
            Argument(key, DynamicValueType.STRING),
            Argument(value, DynamicValueType.OBJECT)
        ])

    def has_unique_elements(self) -> tuple:
        """Check if all elements in the list are unique"""
        return ("has unique elements", [])

    def is_sublist_of(self, superlist: Union[List[Any], DynamicValue]) -> tuple:
        """Check if list is a sublist of another list"""
        if isinstance(superlist, DynamicValue):
            if superlist.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{superlist.name}' has type {superlist.value_type.value}, but list was expected")
            return ("is a sublist of", [Argument(superlist, DynamicValueType.LIST)])
        return ("is a sublist of", [[Argument(v, DynamicValueType.OBJECT) for v in superlist]])

    def is_superlist_of(self, sublist: Union[List[Any], DynamicValue]) -> tuple:
        """Check if list contains another list as a sublist"""
        if isinstance(sublist, DynamicValue):
            if sublist.value_type != DynamicValueType.LIST:
                raise TypeMismatchError(f"Dynamic value '{sublist.name}' has type {sublist.value_type.value}, but list was expected")
            return ("is a superlist of", [Argument(sublist, DynamicValueType.LIST)])
        return ("is a superlist of", [[Argument(v, DynamicValueType.OBJECT) for v in sublist]])
