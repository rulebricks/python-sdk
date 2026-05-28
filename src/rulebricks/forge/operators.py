from typing import Any, Union, List, Optional, Generic, TypeVar
from datetime import datetime
from .types import OperatorDef, OperatorArg, Field, VocabularyValueType, TypeMismatchError
from .vocabulary import VocabularyValue

T = TypeVar('T')
U = TypeVar('U')  # For handling nested generic types

class Argument(Generic[T]):
    """Represents a value that could be either a primitive or vocabulary value"""
    def __init__(self, value: Union[T, VocabularyValue], expected_type: VocabularyValueType):
        self.value = value
        self.expected_type = expected_type
        self._validate_type()

    def _validate_type(self) -> None:
        """Validate that the value matches the expected type"""
        if isinstance(self.value, VocabularyValue):
            if self.value.value_type != self.expected_type:
                raise TypeMismatchError(
                    f"Vocabulary value '{self.value.name}' has type {self.value.value_type.value}, "
                    f"but {self.expected_type.value} was expected"
                )
        else:
            expected_python_type = VocabularyValue.get_expected_type(self.expected_type)
            if not isinstance(self.value, expected_python_type):
                actual_type = type(self.value).__name__
                raise TypeMismatchError(
                    f"Value {self.value} has type {actual_type}, "
                    f"but {self.expected_type.value} was expected"
                )

    def to_dict(self) -> Any:
        """Return the primitive value or vocabulary value dict"""
        if isinstance(self.value, VocabularyValue):
            return self.value.to_dict()
        return self.value  # Return the primitive value directly

    @classmethod
    def process(cls, arg: Any, expected_type: VocabularyValueType) -> Any:
        """Process any argument into the correct format for conditions"""
        if isinstance(arg, Argument):
            return arg.to_dict()
        elif isinstance(arg, VocabularyValue):
            return arg.to_dict()
        elif isinstance(arg, list):
            return [cls.process(item, expected_type) for item in arg]
        elif isinstance(arg, dict):
            return {k: cls.process(v, expected_type) for k, v in arg.items()}
        return arg

    def __repr__(self) -> str:
        if isinstance(self.value, VocabularyValue):
            return f"<{self.value.name.upper()}>"
        return f"{self.value}"

class BooleanField(Field):
    """Valid boolean comparisons/operations in Rulebricks"""
    def __init__(self, name: str, description: str = "", default: bool = False):
            super().__init__(name, description, default)
            self.operators = {
                "any": OperatorDef("any", [], "Match any boolean value", skip_typecheck=True),
                "is_true": OperatorDef("is true", [], "Check if value is true"),
                "is_false": OperatorDef("is false", [], "Check if value is false"),
                "is_null": OperatorDef("is null", [], "Check if value is null")
            }

    def equals(self, value: Union[bool, VocabularyValue]) -> tuple:
        """Check if value equals the given boolean"""
        op_name = "is true" if value else "is false"
        return (op_name, [])

    def is_null(self) -> tuple:
        return ("is null", [])

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
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def equals(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("equals", [Argument(value, VocabularyValueType.NUMBER)])

    def not_equals(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("does not equal", [Argument(value, VocabularyValueType.NUMBER)])

    def greater_than(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("greater than", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("less than", [Argument(value, VocabularyValueType.NUMBER)])

    def greater_than_or_equal(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("greater than or equal to", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than_or_equal(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("less than or equal to", [Argument(value, VocabularyValueType.NUMBER)])

    def between(self, start: Union[int, float, VocabularyValue], end: Union[int, float, VocabularyValue]) -> tuple:
        start_arg = Argument(start, VocabularyValueType.NUMBER)
        end_arg = Argument(end, VocabularyValueType.NUMBER)
        if not isinstance(start, VocabularyValue) and not isinstance(end, VocabularyValue):
            op = self.operators["between"]
            if op.validate and not op.validate([start, end]):
                raise ValueError(f"Invalid range for between: start ({start}) must be less than end ({end})")
        return ("between", [start_arg, end_arg])

    def not_between(self, start: Union[int, float, VocabularyValue], end: Union[int, float, VocabularyValue]) -> tuple:
        start_arg = Argument(start, VocabularyValueType.NUMBER)
        end_arg = Argument(end, VocabularyValueType.NUMBER)
        if not isinstance(start, VocabularyValue) and not isinstance(end, VocabularyValue):
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

    def is_multiple_of(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("is a multiple of", [Argument(value, VocabularyValueType.NUMBER)])

    def is_not_multiple_of(self, value: Union[int, float, VocabularyValue]) -> tuple:
        return ("is not a multiple of", [Argument(value, VocabularyValueType.NUMBER)])

    def is_power_of(self, base: Union[int, float, VocabularyValue]) -> tuple:
        if not isinstance(base, VocabularyValue):
            op = self.operators["is_power_of"]
            if op.validate and not op.validate([base]):
                raise ValueError(f"Invalid base for is power of: {base}. Base must be positive.")
        return ("is a power of", [Argument(base, VocabularyValueType.NUMBER)])

    def is_null(self) -> tuple:
        return ("is null", [])

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
            "equals_case_insensitive": OperatorDef(
                "equals (case-insensitive)",
                [OperatorArg("value", "string", "The value to compare against")]
            ),
            "does_not_equal": OperatorDef("does not equal", [OperatorArg("value", "string", "The value to compare against")]),
            "does_not_equal_case_insensitive": OperatorDef(
                "does not equal (case-insensitive)",
                [OperatorArg("value", "string", "The value to compare against")]
            ),
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
            "contains_any_of": OperatorDef(
                "contains any of",
                [OperatorArg("value", "list", "A list of values the string should contain at least one of", validate=lambda v: len(v) > 0)]
            ),
            "does_not_contain_any_of": OperatorDef(
                "does not contain any of",
                [OperatorArg("value", "list", "A list of values the string should not contain", validate=lambda v: len(v) > 0)]
            ),
            "is_of_length": OperatorDef(
                "is of length",
                [OperatorArg("length", "number", "The length the string should be", validate=lambda v: v > 0)]
            ),
            "is_not_of_length": OperatorDef(
                "is not of length",
                [OperatorArg("length", "number", "The length the string should not be", validate=lambda v: v > 0)]
            ),
            "is_longer_than": OperatorDef(
                "is longer than",
                [OperatorArg("length", "number", "The length the string should be longer than", validate=lambda v: v > 0)]
            ),
            "is_shorter_than": OperatorDef(
                "is shorter than",
                [OperatorArg("length", "number", "The length the string should be shorter than", validate=lambda v: v > 0)]
            ),
            "is_longer_than_or_equal": OperatorDef(
                "is longer than or equal to",
                [OperatorArg("length", "number", "The length the string should be longer than or equal to", validate=lambda v: v > 0)]
            ),
            "is_shorter_than_or_equal": OperatorDef(
                "is shorter than or equal to",
                [OperatorArg("length", "number", "The length the string should be shorter than or equal to", validate=lambda v: v > 0)]
            ),
            "starts_with_case_insensitive": OperatorDef(
                "starts with (case-insensitive)",
                [OperatorArg("prefix", "string", "The string that the value should start with (case-insensitive)")]
            ),
            "ends_with_case_insensitive": OperatorDef(
                "ends with (case-insensitive)",
                [OperatorArg("suffix", "string", "The string that the value should end with (case-insensitive)")]
            ),
            "contains_case_insensitive": OperatorDef(
                "contains (case-insensitive)",
                [OperatorArg("substring", "string", "The string that should be contained within the value (case-insensitive)")]
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
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def contains(self, value: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(value, VocabularyValueType.STRING)
        if not isinstance(value, VocabularyValue):
            op = self.operators["contains"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for contains: {value}")
        return ("contains", [arg])

    def not_contains(self, value: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(value, VocabularyValueType.STRING)
        if not isinstance(value, VocabularyValue):
            op = self.operators["does_not_contain"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for does not contain: {value}")
        return ("does not contain", [arg])

    def equals(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("equals", [Argument(value, VocabularyValueType.STRING)])

    def equals_case_insensitive(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("equals (case-insensitive)", [Argument(value, VocabularyValueType.STRING)])

    def not_equals(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("does not equal", [Argument(value, VocabularyValueType.STRING)])

    def not_equals_case_insensitive(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("does not equal (case-insensitive)", [Argument(value, VocabularyValueType.STRING)])

    def is_empty(self) -> tuple:
        return ("is empty", [])

    def is_not_empty(self) -> tuple:
        return ("is not empty", [])

    def starts_with(self, value: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(value, VocabularyValueType.STRING)
        if not isinstance(value, VocabularyValue):
            op = self.operators["starts_with"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for starts with: {value}")
        return ("starts with", [arg])

    def ends_with(self, value: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(value, VocabularyValueType.STRING)
        if not isinstance(value, VocabularyValue):
            op = self.operators["ends_with"]
            if op.args[0].validate and not op.args[0].validate(value):
                raise ValueError(f"Invalid value for ends with: {value}")
        return ("ends with", [arg])

    def contains_case_insensitive(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("contains (case-insensitive)", [Argument(value, VocabularyValueType.STRING)])

    def starts_with_case_insensitive(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("starts with (case-insensitive)", [Argument(value, VocabularyValueType.STRING)])

    def ends_with_case_insensitive(self, value: Union[str, VocabularyValue]) -> tuple:
        return ("ends with (case-insensitive)", [Argument(value, VocabularyValueType.STRING)])

    def is_included_in(self, values: Union[List[str], List[VocabularyValue], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(
                    f"Vocabulary value '{values.name}' has type {values.value_type.value}, "
                    f"but list was expected"
                )
            return ("is included in", [Argument(values, VocabularyValueType.LIST)])

        op = self.operators["is_included_in"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")

        return ("is included in", [[Argument(v, VocabularyValueType.STRING) for v in values]])

    def is_not_included_in(self, values: Union[List[str], List[VocabularyValue], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(
                    f"Vocabulary value '{values.name}' has type {values.value_type.value}, "
                    f"but list was expected"
                )
            return ("is not included in", [Argument(values, VocabularyValueType.LIST)])

        op = self.operators["is_not_included_in"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")

        return ("is not included in", [[Argument(v, VocabularyValueType.STRING) for v in values]])

    def contains_any_of(self, values: Union[List[str], List[VocabularyValue], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(
                    f"Vocabulary value '{values.name}' has type {values.value_type.value}, "
                    f"but list was expected"
                )
            return ("contains any of", [Argument(values, VocabularyValueType.LIST)])

        op = self.operators["contains_any_of"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")

        return ("contains any of", [[Argument(v, VocabularyValueType.STRING) for v in values]])

    def not_contains_any_of(self, values: Union[List[str], List[VocabularyValue], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(
                    f"Vocabulary value '{values.name}' has type {values.value_type.value}, "
                    f"but list was expected"
                )
            return ("does not contain any of", [Argument(values, VocabularyValueType.LIST)])

        op = self.operators["does_not_contain_any_of"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")

        return ("does not contain any of", [[Argument(v, VocabularyValueType.STRING) for v in values]])

    def does_not_contain_any_of(self, values: Union[List[str], List[VocabularyValue], VocabularyValue]) -> tuple:
        return self.not_contains_any_of(values)

    def length_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is of length", [Argument(length, VocabularyValueType.NUMBER)])

    def is_of_length(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.length_equals(length)

    def length_not_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is not of length", [Argument(length, VocabularyValueType.NUMBER)])

    def is_not_of_length(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.length_not_equals(length)

    def longer_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is longer than", [Argument(length, VocabularyValueType.NUMBER)])

    def is_longer_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.longer_than(length)

    def shorter_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is shorter than", [Argument(length, VocabularyValueType.NUMBER)])

    def is_shorter_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.shorter_than(length)

    def longer_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is longer than or equal to", [Argument(length, VocabularyValueType.NUMBER)])

    def is_longer_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.longer_than_or_equal(length)

    def shorter_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is shorter than or equal to", [Argument(length, VocabularyValueType.NUMBER)])

    def is_shorter_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.shorter_than_or_equal(length)

    def matches_regex(self, pattern: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(pattern, VocabularyValueType.STRING)
        if not isinstance(pattern, VocabularyValue):
            op = self.operators["matches_regex"]
            if op.args[0].validate and not op.args[0].validate(pattern):
                raise ValueError(f"Invalid regex pattern: {pattern}")
        return ("matches RegEx", [arg])

    def not_matches_regex(self, pattern: Union[str, VocabularyValue]) -> tuple:
        arg = Argument(pattern, VocabularyValueType.STRING)
        if not isinstance(pattern, VocabularyValue):
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

    def is_null(self) -> tuple:
        return ("is null", [])

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
            "between_n_and_m_days_ago": OperatorDef(
                "is between N and M days ago",
                [
                    OperatorArg("minDays", "number", "Minimum number of days ago", placeholder="Min days"),
                    OperatorArg("maxDays", "number", "Maximum number of days ago", placeholder="Max days")
                ]
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
            "months_ago": OperatorDef(
                "months ago",
                [OperatorArg("months", "number", "Number of months ago that the date is equal to")]
            ),
            "less_than_months_ago": OperatorDef(
                "is less than N months ago",
                [OperatorArg("months", "number", "Number of months ago that the date is less than or equal to")]
            ),
            "more_than_months_ago": OperatorDef(
                "is more than N months ago",
                [OperatorArg("months", "number", "Number of months ago that the date is more than or equal to")]
            ),
            "between_n_and_m_months_ago": OperatorDef(
                "is between N and M months ago",
                [
                    OperatorArg("minMonths", "number", "Minimum number of months ago", placeholder="Min months"),
                    OperatorArg("maxMonths", "number", "Maximum number of months ago", placeholder="Max months")
                ]
            ),
            "months_from_now": OperatorDef(
                "months from now",
                [OperatorArg("months", "number", "Number of months from now that the date is equal to")]
            ),
            "less_than_months_from_now": OperatorDef(
                "is less than N months from now",
                [OperatorArg("months", "number", "Number of months from now that the date is less than or equal to")]
            ),
            "more_than_months_from_now": OperatorDef(
                "is more than N months from now",
                [OperatorArg("months", "number", "Number of months from now that the date is more than or equal to")]
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
            "equals": OperatorDef(
                "equals",
                [OperatorArg("date", "date", "Date that value must be equal to")]
            ),
            "does_not_equal": OperatorDef(
                "does not equal",
                [OperatorArg("date", "date", "Date that value must not be equal to")]
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
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def is_past(self) -> tuple:
        return ("is in the past", [])

    def is_future(self) -> tuple:
        return ("is in the future", [])

    def days_ago(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("days ago", [Argument(days, VocabularyValueType.NUMBER)])

    def less_than_days_ago(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N days ago", [Argument(days, VocabularyValueType.NUMBER)])

    def more_than_days_ago(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N days ago", [Argument(days, VocabularyValueType.NUMBER)])

    def between_n_and_m_days_ago(self, min_days: Union[int, VocabularyValue], max_days: Union[int, VocabularyValue]) -> tuple:
        return (
            "is between N and M days ago",
            [Argument(min_days, VocabularyValueType.NUMBER), Argument(max_days, VocabularyValueType.NUMBER)]
        )

    def days_from_now(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("days from now", [Argument(days, VocabularyValueType.NUMBER)])

    def less_than_days_from_now(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N days from now", [Argument(days, VocabularyValueType.NUMBER)])

    def more_than_days_from_now(self, days: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N days from now", [Argument(days, VocabularyValueType.NUMBER)])

    def months_ago(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("months ago", [Argument(months, VocabularyValueType.NUMBER)])

    def less_than_months_ago(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N months ago", [Argument(months, VocabularyValueType.NUMBER)])

    def more_than_months_ago(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N months ago", [Argument(months, VocabularyValueType.NUMBER)])

    def between_n_and_m_months_ago(self, min_months: Union[int, VocabularyValue], max_months: Union[int, VocabularyValue]) -> tuple:
        return (
            "is between N and M months ago",
            [Argument(min_months, VocabularyValueType.NUMBER), Argument(max_months, VocabularyValueType.NUMBER)]
        )

    def months_from_now(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("months from now", [Argument(months, VocabularyValueType.NUMBER)])

    def less_than_months_from_now(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N months from now", [Argument(months, VocabularyValueType.NUMBER)])

    def more_than_months_from_now(self, months: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N months from now", [Argument(months, VocabularyValueType.NUMBER)])

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

    def after(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("after", [Argument(date, VocabularyValueType.DATE)])

    def on_or_after(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("on or after", [Argument(date, VocabularyValueType.DATE)])

    def before(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("before", [Argument(date, VocabularyValueType.DATE)])

    def on_or_before(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("on or before", [Argument(date, VocabularyValueType.DATE)])

    def equals(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("equals", [Argument(date, VocabularyValueType.DATE)])

    def not_equals(self, date: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("does not equal", [Argument(date, VocabularyValueType.DATE)])

    def between(self, start: Union[datetime, str, VocabularyValue], end: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("between", [Argument(start, VocabularyValueType.DATE), Argument(end, VocabularyValueType.DATE)])

    def not_between(self, start: Union[datetime, str, VocabularyValue], end: Union[datetime, str, VocabularyValue]) -> tuple:
        return ("not between", [Argument(start, VocabularyValueType.DATE), Argument(end, VocabularyValueType.DATE)])

    def is_null(self) -> tuple:
        return ("is null", [])

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
            ),
            "does_not_contain_object_with_key_value": OperatorDef(
                "does not contain object with key & value",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg("value", "generic", "Value that the key must not be equal to")
                ]
            ),
            "contains_object_with_key": OperatorDef(
                "contains object with key",
                [OperatorArg("key", "string", "Key of any object contained in the list")]
            ),
            "does_not_contain_object_with_key": OperatorDef(
                "does not contain object with key",
                [OperatorArg("key", "string", "Key of any object contained in the list")]
            ),
            "has_unique_elements": OperatorDef("has unique elements", [], "Check if all elements in the list are unique"),
            "is_sublist_of": OperatorDef(
                "is a sublist of",
                [OperatorArg("superlist", "list", "List that must contain this list as a sublist")]
            ),
            "is_superlist_of": OperatorDef(
                "is a superlist of",
                [OperatorArg("sublist", "list", "List that must be contained as a sublist within this list")]
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def contains(self, value: Union[Any, VocabularyValue]) -> tuple:
        return ("contains", [Argument(value, VocabularyValueType.OBJECT)])  # Use OBJECT type for generic values

    def is_empty(self) -> tuple:
        return ("is empty", [])

    def is_not_empty(self) -> tuple:
        return ("is not empty", [])

    def length_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is of length", [Argument(length, VocabularyValueType.NUMBER)])

    def length_not_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is not of length", [Argument(length, VocabularyValueType.NUMBER)])

    def longer_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is longer than", [Argument(length, VocabularyValueType.NUMBER)])

    def shorter_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return ("is shorter than", [Argument(length, VocabularyValueType.NUMBER)])

    def contains_all(self, values: Union[List[Any], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains all of", [Argument(values, VocabularyValueType.LIST)])
        return ("contains all of", [[Argument(v, VocabularyValueType.OBJECT) for v in values]])

    def contains_any(self, values: Union[List[Any], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains any of", [Argument(values, VocabularyValueType.LIST)])
        return ("contains any of", [[Argument(v, VocabularyValueType.OBJECT) for v in values]])

    def contains_none(self, values: Union[List[Any], VocabularyValue]) -> tuple:
        if isinstance(values, VocabularyValue):
            if values.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{values.name}' has type {values.value_type.value}, but list was expected")
            return ("contains none of", [Argument(values, VocabularyValueType.LIST)])
        return ("contains none of", [[Argument(v, VocabularyValueType.OBJECT) for v in values]])

    def not_contains(self, value: Union[Any, VocabularyValue]) -> tuple:
        """Check if list does not contain value"""
        return ("does not contain", [Argument(value, VocabularyValueType.OBJECT)])

    def equals(self, other: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list equals another list"""
        if isinstance(other, VocabularyValue):
            if other.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{other.name}' has type {other.value_type.value}, but list was expected")
            return ("is equal to", [Argument(other, VocabularyValueType.LIST)])
        return ("is equal to", [[Argument(v, VocabularyValueType.OBJECT) for v in other]])

    def not_equals(self, other: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list does not equal another list"""
        if isinstance(other, VocabularyValue):
            if other.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{other.name}' has type {other.value_type.value}, but list was expected")
            return ("is not equal to", [Argument(other, VocabularyValueType.LIST)])
        return ("is not equal to", [[Argument(v, VocabularyValueType.OBJECT) for v in other]])

    def has_duplicates(self) -> tuple:
        """Check if list has duplicate values"""
        return ("contains duplicates", [])

    def no_duplicates(self) -> tuple:
        """Check if list has no duplicate values"""
        return ("does not contain duplicates", [])

    def contains_object_with_key_value(self, key: Union[str, VocabularyValue], value: Union[Any, VocabularyValue]) -> tuple:
        """Check if list contains an object with specified key and value"""
        return ("contains object with key & value", [
            Argument(key, VocabularyValueType.STRING),
            Argument(value, VocabularyValueType.OBJECT)
        ])

    def does_not_contain_object_with_key_value(self, key: Union[str, VocabularyValue], value: Union[Any, VocabularyValue]) -> tuple:
        """Check if list does not contain an object with specified key and value"""
        return ("does not contain object with key & value", [
            Argument(key, VocabularyValueType.STRING),
            Argument(value, VocabularyValueType.OBJECT)
        ])

    def contains_object_with_key(self, key: Union[str, VocabularyValue]) -> tuple:
        """Check if list contains an object with specified key"""
        return ("contains object with key", [Argument(key, VocabularyValueType.STRING)])

    def does_not_contain_object_with_key(self, key: Union[str, VocabularyValue]) -> tuple:
        """Check if list does not contain an object with specified key"""
        return ("does not contain object with key", [Argument(key, VocabularyValueType.STRING)])

    def has_unique_elements(self) -> tuple:
        """Check if all elements in the list are unique"""
        return ("has unique elements", [])

    def is_sublist_of(self, superlist: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list is a sublist of another list"""
        if isinstance(superlist, VocabularyValue):
            if superlist.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{superlist.name}' has type {superlist.value_type.value}, but list was expected")
            return ("is a sublist of", [Argument(superlist, VocabularyValueType.LIST)])
        return ("is a sublist of", [[Argument(v, VocabularyValueType.OBJECT) for v in superlist]])

    def is_superlist_of(self, sublist: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list contains another list as a sublist"""
        if isinstance(sublist, VocabularyValue):
            if sublist.value_type != VocabularyValueType.LIST:
                raise TypeMismatchError(f"Vocabulary value '{sublist.name}' has type {sublist.value_type.value}, but list was expected")
            return ("is a superlist of", [Argument(sublist, VocabularyValueType.LIST)])
        return ("is a superlist of", [[Argument(v, VocabularyValueType.OBJECT) for v in sublist]])

    def is_null(self) -> tuple:
        return ("is null", [])
