import math
from datetime import datetime
from typing import Any, Union, List, Optional, Generic, TypeVar

from .types import OperatorDef, OperatorArg, Field, VocabularyValueType, TypeMismatchError
from .vocabulary import VocabularyValue

T = TypeVar('T')
U = TypeVar('U')  # For handling nested generic types

class Argument(Generic[T]):
    """Represents a value that could be either a primitive or vocabulary value"""
    def __init__(
        self,
        value: Union[T, VocabularyValue],
        expected_type: Optional[VocabularyValueType] = None
    ):
        self.value = value
        self.expected_type = expected_type
        self._validate_type()

    def _validate_type(self) -> None:
        """Validate that the value matches the expected type"""
        if self.expected_type is None:
            if not self._is_valid_generic_literal(self.value):
                raise TypeMismatchError(
                    f"Value {self.value} is not a valid generic literal"
                )
            return

        if isinstance(self.value, VocabularyValue):
            if self.value.value_type != self.expected_type:
                raise TypeMismatchError(
                    f"Vocabulary value '{self.value.name}' has type {self.value.value_type.value}, "
                    f"but {self.expected_type.value} was expected"
                )
        else:
            if self.expected_type == VocabularyValueType.DATE:
                is_valid = isinstance(self.value, (datetime, str))
            elif self.expected_type == VocabularyValueType.NUMBER:
                is_valid = (
                    isinstance(self.value, (int, float))
                    and not isinstance(self.value, bool)
                    and (
                        not isinstance(self.value, float)
                        or math.isfinite(self.value)
                    )
                )
            elif self.expected_type == VocabularyValueType.LIST:
                is_valid = (
                    isinstance(self.value, list)
                    and self._is_valid_generic_literal(self.value)
                )
            elif self.expected_type == VocabularyValueType.OBJECT:
                is_valid = (
                    isinstance(self.value, dict)
                    and self._is_valid_generic_literal(self.value)
                )
            elif self.expected_type == VocabularyValueType.FUNCTION:
                is_valid = callable(self.value)
            else:
                expected_python_type = VocabularyValue.get_expected_type(self.expected_type)
                is_valid = isinstance(self.value, expected_python_type)

            if not is_valid:
                actual_type = type(self.value).__name__
                raise TypeMismatchError(
                    f"Value {self.value} has type {actual_type}, "
                    f"but {self.expected_type.value} was expected"
                )

    @classmethod
    def _is_valid_generic_literal(
        cls,
        value: Any,
        seen: Optional[set] = None
    ) -> bool:
        """Return whether a value can be represented safely in a condition payload."""
        if isinstance(value, VocabularyValue) or value is None:
            return True
        if isinstance(value, (str, bool)):
            return True
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            return not isinstance(value, float) or math.isfinite(value)

        seen = seen or set()
        if isinstance(value, list):
            identity = id(value)
            if identity in seen:
                return False
            seen.add(identity)
            is_valid = all(cls._is_valid_generic_literal(item, seen) for item in value)
            seen.remove(identity)
            return is_valid

        if isinstance(value, dict):
            identity = id(value)
            if identity in seen:
                return False
            seen.add(identity)
            is_valid = all(
                isinstance(key, str)
                and cls._is_valid_generic_literal(item, seen)
                for key, item in value.items()
            )
            seen.remove(identity)
            return is_valid

        return False

    def to_dict(self) -> Any:
        """Return the primitive value or vocabulary value dict"""
        if isinstance(self.value, VocabularyValue):
            return self.value.to_dict()
        if isinstance(self.value, list):
            return [self.process(item) for item in self.value]
        if isinstance(self.value, dict):
            return {key: self.process(value) for key, value in self.value.items()}
        return self.value  # Return the primitive value directly

    @classmethod
    def process(
        cls,
        arg: Any,
        expected_type: Optional[VocabularyValueType] = None
    ) -> Any:
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

    def equals(self, value: bool) -> tuple:
        """Check if value equals the given boolean"""
        if isinstance(value, VocabularyValue):
            raise TypeMismatchError(
                "BooleanField.equals requires a literal bool; "
                f"vocabulary value '{value.name}' is not supported"
            )
        if type(value) is not bool:
            raise TypeMismatchError(
                "BooleanField.equals requires a literal bool, "
                f"but {type(value).__name__} was provided"
            )
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
                [OperatorArg("base", "number", "The base number")]
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
            "is_phone": OperatorDef("is a valid phone number", []),
            "is_zip_code": OperatorDef("is a valid zip code", []),
            "matches_regex": OperatorDef(
                "matches RegEx",
                [
                    OperatorArg(
                        "regex",
                        "string",
                        "The regex the string should match",
                        placeholder="^[a-z]+$",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "does_not_match_regex": OperatorDef(
                "does not match RegEx",
                [
                    OperatorArg(
                        "regex",
                        "string",
                        "The regex the string should match",
                        placeholder="^[a-z]+$",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "is_work_email": OperatorDef("is a work email address", []),
            "is_personal_email": OperatorDef("is a personal email address", []),
            "is_valid_email": OperatorDef("is a valid email address", [], "Check if string is a valid email address"),
            "is_not_valid_email": OperatorDef("is not a valid email address", [], "Check if string is not a valid email address"),
            "is_valid_url": OperatorDef("is a valid URL", [], "Check if string is a valid URL"),
            "is_not_valid_url": OperatorDef("is not a valid URL", [], "Check if string is not a valid URL"),
            "is_valid_ip": OperatorDef("is a valid IP address", [], "Check if string is a valid IP address"),
            "is_not_valid_ip": OperatorDef("is not a valid IP address", [], "Check if string is not a valid IP address"),
            "is_ipv6": OperatorDef("is a valid IPV6 address", []),
            "is_not_ipv6": OperatorDef("is not a valid IPV6 address", []),
            "is_credit_card": OperatorDef("is a valid credit card number", []),
            "is_not_credit_card": OperatorDef("is not a valid credit card number", []),
            "is_country_code": OperatorDef("is a valid country code", []),
            "is_not_country_code": OperatorDef("is not a valid country code", []),
            "contains_profanity": OperatorDef("contains profanity", []),
            "does_not_contain_profanity": OperatorDef("does not contain profanity", []),
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
            "version_greater_than": OperatorDef(
                "version is greater than",
                [
                    OperatorArg(
                        "version",
                        "string",
                        "The version to compare against (e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "version_less_than": OperatorDef(
                "version is less than",
                [
                    OperatorArg(
                        "version",
                        "string",
                        "The version to compare against (e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "version_equals": OperatorDef(
                "version is equal to",
                [
                    OperatorArg(
                        "version",
                        "string",
                        "The version to compare against (e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "version_greater_than_or_equal": OperatorDef(
                "version is greater than or equal to",
                [
                    OperatorArg(
                        "version",
                        "string",
                        "The version to compare against (e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "version_less_than_or_equal": OperatorDef(
                "version is less than or equal to",
                [
                    OperatorArg(
                        "version",
                        "string",
                        "The version to compare against (e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "version_between": OperatorDef(
                "version is between",
                [
                    OperatorArg(
                        "minVersion",
                        "string",
                        "The minimum version (inclusive, e.g., 1.2.3)",
                        validate=lambda v: len(v) > 0
                    ),
                    OperatorArg(
                        "maxVersion",
                        "string",
                        "The maximum version (inclusive, e.g., 2.0.0)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "is_valid_semantic_version": OperatorDef("is valid semantic version", []),
            "satisfies_version_range": OperatorDef(
                "satisfies version range",
                [
                    OperatorArg(
                        "range",
                        "string",
                        "The version range (e.g., >=1.2.3 <2.0.0 or ^1.2.3)",
                        validate=lambda v: len(v) > 0
                    )
                ]
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def _validated_argument(
        self,
        operator_key: str,
        value: Any,
        expected_type: VocabularyValueType,
        arg_index: int = 0
    ) -> Argument:
        arg = Argument(value, expected_type)
        if not isinstance(value, VocabularyValue):
            validate = self.operators[operator_key].args[arg_index].validate
            if validate and not validate(value):
                raise ValueError(
                    f"Invalid value for {self.operators[operator_key].name}: {value}"
                )
        return arg

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

    def is_included_in(
        self,
        values: Union[List[Union[str, VocabularyValue]], VocabularyValue]
    ) -> tuple:
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

    def is_not_included_in(
        self,
        values: Union[List[Union[str, VocabularyValue]], VocabularyValue]
    ) -> tuple:
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

    def contains_any_of(
        self,
        values: Union[List[Union[str, VocabularyValue]], VocabularyValue]
    ) -> tuple:
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

    def not_contains_any_of(
        self,
        values: Union[List[Union[str, VocabularyValue]], VocabularyValue]
    ) -> tuple:
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

    def does_not_contain_any_of(
        self,
        values: Union[List[Union[str, VocabularyValue]], VocabularyValue]
    ) -> tuple:
        return self.not_contains_any_of(values)

    def length_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is of length",
            [self._validated_argument("is_of_length", length, VocabularyValueType.NUMBER)]
        )

    def is_of_length(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.length_equals(length)

    def length_not_equals(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is not of length",
            [self._validated_argument("is_not_of_length", length, VocabularyValueType.NUMBER)]
        )

    def is_not_of_length(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.length_not_equals(length)

    def longer_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is longer than",
            [self._validated_argument("is_longer_than", length, VocabularyValueType.NUMBER)]
        )

    def is_longer_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.longer_than(length)

    def shorter_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is shorter than",
            [self._validated_argument("is_shorter_than", length, VocabularyValueType.NUMBER)]
        )

    def is_shorter_than(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.shorter_than(length)

    def longer_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is longer than or equal to",
            [
                self._validated_argument(
                    "is_longer_than_or_equal",
                    length,
                    VocabularyValueType.NUMBER
                )
            ]
        )

    def is_longer_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return self.longer_than_or_equal(length)

    def shorter_than_or_equal(self, length: Union[int, VocabularyValue]) -> tuple:
        return (
            "is shorter than or equal to",
            [
                self._validated_argument(
                    "is_shorter_than_or_equal",
                    length,
                    VocabularyValueType.NUMBER
                )
            ]
        )

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

    def is_phone(self) -> tuple:
        return ("is a valid phone number", [])

    def is_zip_code(self) -> tuple:
        return ("is a valid zip code", [])

    def is_work_email(self) -> tuple:
        return ("is a work email address", [])

    def is_personal_email(self) -> tuple:
        return ("is a personal email address", [])

    def is_ipv6(self) -> tuple:
        return ("is a valid IPV6 address", [])

    def is_not_ipv6(self) -> tuple:
        return ("is not a valid IPV6 address", [])

    def is_credit_card(self) -> tuple:
        return ("is a valid credit card number", [])

    def is_not_credit_card(self) -> tuple:
        return ("is not a valid credit card number", [])

    def is_country_code(self) -> tuple:
        return ("is a valid country code", [])

    def is_not_country_code(self) -> tuple:
        return ("is not a valid country code", [])

    def contains_profanity(self) -> tuple:
        return ("contains profanity", [])

    def does_not_contain_profanity(self) -> tuple:
        return ("does not contain profanity", [])

    def version_greater_than(
        self,
        version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is greater than",
            [
                self._validated_argument(
                    "version_greater_than",
                    version,
                    VocabularyValueType.STRING
                )
            ]
        )

    def version_less_than(
        self,
        version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is less than",
            [
                self._validated_argument(
                    "version_less_than",
                    version,
                    VocabularyValueType.STRING
                )
            ]
        )

    def version_equals(
        self,
        version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is equal to",
            [
                self._validated_argument(
                    "version_equals",
                    version,
                    VocabularyValueType.STRING
                )
            ]
        )

    def version_greater_than_or_equal(
        self,
        version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is greater than or equal to",
            [
                self._validated_argument(
                    "version_greater_than_or_equal",
                    version,
                    VocabularyValueType.STRING
                )
            ]
        )

    def version_less_than_or_equal(
        self,
        version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is less than or equal to",
            [
                self._validated_argument(
                    "version_less_than_or_equal",
                    version,
                    VocabularyValueType.STRING
                )
            ]
        )

    def version_between(
        self,
        min_version: Union[str, VocabularyValue],
        max_version: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "version is between",
            [
                self._validated_argument(
                    "version_between",
                    min_version,
                    VocabularyValueType.STRING
                ),
                self._validated_argument(
                    "version_between",
                    max_version,
                    VocabularyValueType.STRING,
                    1
                )
            ]
        )

    def is_valid_semantic_version(self) -> tuple:
        return ("is valid semantic version", [])

    def satisfies_version_range(
        self,
        version_range: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "satisfies version range",
            [
                self._validated_argument(
                    "satisfies_version_range",
                    version_range,
                    VocabularyValueType.STRING
                )
            ]
        )

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
                [OperatorArg("value", "number", "Number of days ago that the date is equal to")]
            ),
            "less_than_days_ago": OperatorDef(
                "is less than N days ago",
                [OperatorArg("value", "number", "Number of days ago that the date is less than or equal to")]
            ),
            "more_than_days_ago": OperatorDef(
                "is more than N days ago",
                [OperatorArg("value", "number", "Number of days ago that the date is more than or equal to")]
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
                [OperatorArg("value", "number", "Number of days from now that the date is equal to")]
            ),
            "less_than_days_from_now": OperatorDef(
                "is less than N days from now",
                [OperatorArg("value", "number", "Number of days from now that the date is less than or equal to")]
            ),
            "more_than_days_from_now": OperatorDef(
                "is more than N days from now",
                [OperatorArg("value", "number", "Number of days from now that the date is more than or equal to")]
            ),
            "months_ago": OperatorDef(
                "months ago",
                [OperatorArg("value", "number", "Number of months ago that the date is equal to")]
            ),
            "less_than_months_ago": OperatorDef(
                "is less than N months ago",
                [OperatorArg("value", "number", "Number of months ago that the date is less than or equal to")]
            ),
            "more_than_months_ago": OperatorDef(
                "is more than N months ago",
                [OperatorArg("value", "number", "Number of months ago that the date is more than or equal to")]
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
                [OperatorArg("value", "number", "Number of months from now that the date is equal to")]
            ),
            "less_than_months_from_now": OperatorDef(
                "is less than N months from now",
                [OperatorArg("value", "number", "Number of months from now that the date is less than or equal to")]
            ),
            "more_than_months_from_now": OperatorDef(
                "is more than N months from now",
                [OperatorArg("value", "number", "Number of months from now that the date is more than or equal to")]
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
                [OperatorArg("value", "date", "Date that value must be after")]
            ),
            "on_or_after": OperatorDef(
                "on or after",
                [OperatorArg("value", "date", "Date that value must be on or after")]
            ),
            "before": OperatorDef(
                "before",
                [OperatorArg("value", "date", "Date that value must be before")]
            ),
            "on_or_before": OperatorDef(
                "on or before",
                [OperatorArg("value", "date", "Date that value must be on or before")]
            ),
            "equals": OperatorDef(
                "equals",
                [OperatorArg("value", "date", "Date that value must be equal to")]
            ),
            "does_not_equal": OperatorDef(
                "does not equal",
                [OperatorArg("value", "date", "Date that value must not be equal to")]
            ),
            "between": OperatorDef(
                "between",
                [
                    OperatorArg("lower", "date", "Date that value must be after", placeholder="From"),
                    OperatorArg("upper", "date", "Date that value must be before", placeholder="To")
                ]
            ),
            "not_between": OperatorDef(
                "not between",
                [
                    OperatorArg("lower", "date", "Date that value must be before", placeholder="From"),
                    OperatorArg("upper", "date", "Date that value must be after", placeholder="To")
                ]
            ),
            "is_before_time": OperatorDef(
                "is before time",
                [
                    OperatorArg(
                        "time",
                        "string",
                        "Time of day that date must be before",
                        placeholder="Enter time (e.g., 2:30 PM)"
                    )
                ]
            ),
            "is_after_time": OperatorDef(
                "is after time",
                [
                    OperatorArg(
                        "time",
                        "string",
                        "Time of day that date must be after",
                        placeholder="Enter time (e.g., 2:30 PM)"
                    )
                ]
            ),
            "hours_ago": OperatorDef(
                "hours ago",
                [OperatorArg("value", "number", "Number of hours ago that the date is equal to")]
            ),
            "less_than_hours_ago": OperatorDef(
                "is less than N hours ago",
                [OperatorArg("value", "number", "Number of hours ago that the date is less than")]
            ),
            "more_than_hours_ago": OperatorDef(
                "is more than N hours ago",
                [OperatorArg("value", "number", "Number of hours ago that the date is more than")]
            ),
            "between_n_and_m_hours_ago": OperatorDef(
                "is between N and M hours ago",
                [
                    OperatorArg("minHours", "number", "Minimum number of hours ago", placeholder="Min hours"),
                    OperatorArg("maxHours", "number", "Maximum number of hours ago", placeholder="Max hours")
                ]
            ),
            "hours_from_now": OperatorDef(
                "hours from now",
                [OperatorArg("value", "number", "Number of hours from now that the date is equal to")]
            ),
            "less_than_hours_from_now": OperatorDef(
                "is less than N hours from now",
                [OperatorArg("value", "number", "Number of hours from now that the date is less than")]
            ),
            "more_than_hours_from_now": OperatorDef(
                "is more than N hours from now",
                [OperatorArg("value", "number", "Number of hours from now that the date is more than")]
            ),
            "minutes_ago": OperatorDef(
                "minutes ago",
                [OperatorArg("value", "number", "Number of minutes ago that the date is equal to")]
            ),
            "less_than_minutes_ago": OperatorDef(
                "is less than N minutes ago",
                [OperatorArg("value", "number", "Number of minutes ago that the date is less than")]
            ),
            "more_than_minutes_ago": OperatorDef(
                "is more than N minutes ago",
                [OperatorArg("value", "number", "Number of minutes ago that the date is more than")]
            ),
            "between_n_and_m_minutes_ago": OperatorDef(
                "is between N and M minutes ago",
                [
                    OperatorArg("minMinutes", "number", "Minimum number of minutes ago", placeholder="Min minutes"),
                    OperatorArg("maxMinutes", "number", "Maximum number of minutes ago", placeholder="Max minutes")
                ]
            ),
            "minutes_from_now": OperatorDef(
                "minutes from now",
                [OperatorArg("value", "number", "Number of minutes from now that the date is equal to")]
            ),
            "less_than_minutes_from_now": OperatorDef(
                "is less than N minutes from now",
                [OperatorArg("value", "number", "Number of minutes from now that the date is less than")]
            ),
            "more_than_minutes_from_now": OperatorDef(
                "is more than N minutes from now",
                [OperatorArg("value", "number", "Number of minutes from now that the date is more than")]
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

    def is_before_time(self, time: Union[str, VocabularyValue]) -> tuple:
        return ("is before time", [Argument(time, VocabularyValueType.STRING)])

    def is_after_time(self, time: Union[str, VocabularyValue]) -> tuple:
        return ("is after time", [Argument(time, VocabularyValueType.STRING)])

    def hours_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("hours ago", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than_hours_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N hours ago", [Argument(value, VocabularyValueType.NUMBER)])

    def more_than_hours_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N hours ago", [Argument(value, VocabularyValueType.NUMBER)])

    def between_n_and_m_hours_ago(
        self,
        min_hours: Union[int, VocabularyValue],
        max_hours: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "is between N and M hours ago",
            [
                Argument(min_hours, VocabularyValueType.NUMBER),
                Argument(max_hours, VocabularyValueType.NUMBER)
            ]
        )

    def hours_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("hours from now", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than_hours_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N hours from now", [Argument(value, VocabularyValueType.NUMBER)])

    def more_than_hours_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N hours from now", [Argument(value, VocabularyValueType.NUMBER)])

    def minutes_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("minutes ago", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than_minutes_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N minutes ago", [Argument(value, VocabularyValueType.NUMBER)])

    def more_than_minutes_ago(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N minutes ago", [Argument(value, VocabularyValueType.NUMBER)])

    def between_n_and_m_minutes_ago(
        self,
        min_minutes: Union[int, VocabularyValue],
        max_minutes: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "is between N and M minutes ago",
            [
                Argument(min_minutes, VocabularyValueType.NUMBER),
                Argument(max_minutes, VocabularyValueType.NUMBER)
            ]
        )

    def minutes_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("minutes from now", [Argument(value, VocabularyValueType.NUMBER)])

    def less_than_minutes_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is less than N minutes from now", [Argument(value, VocabularyValueType.NUMBER)])

    def more_than_minutes_from_now(self, value: Union[int, VocabularyValue]) -> tuple:
        return ("is more than N minutes from now", [Argument(value, VocabularyValueType.NUMBER)])

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
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be contained in the list",
                        placeholder="Enter any value to search for"
                    )
                ]
            ),
            "contains_case_insensitive": OperatorDef(
                "contains (case-insensitive)",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be contained in the list (case-insensitive for strings)",
                        placeholder="Enter any value to search for"
                    )
                ]
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
            "is_longer_than_or_equal": OperatorDef(
                "is longer than or equal to",
                [OperatorArg("length", "number", "Length that the list must be longer than or equal to")]
            ),
            "is_shorter_than_or_equal": OperatorDef(
                "is shorter than or equal to",
                [OperatorArg("length", "number", "Length that the list must be shorter than or equal to")]
            ),
            "contains_all_of": OperatorDef(
                "contains all of",
                [OperatorArg("values", "list", "List of values that must be contained in the list")]
            ),
            "contains_all_of_case_insensitive": OperatorDef(
                "contains all of (case-insensitive)",
                [
                    OperatorArg(
                        "values",
                        "list",
                        "List of values that must be contained in the list (case-insensitive for strings)"
                    )
                ]
            ),
            "contains_n_occurrences_of": OperatorDef(
                "contains N occurrences of",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be contained in the list",
                        placeholder="Enter any value to search for"
                    ),
                    OperatorArg(
                        "occurrences",
                        "number",
                        "Number of occurrences that must be present"
                    )
                ]
            ),
            "contains_at_least_n_occurrences_of": OperatorDef(
                "contains at least N occurrences of",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be contained in the list",
                        placeholder="Enter any value to search for"
                    ),
                    OperatorArg(
                        "occurrences",
                        "number",
                        "Number of occurrences that must be present"
                    )
                ]
            ),
            "contains_at_most_n_occurrences_of": OperatorDef(
                "contains at most N occurrences of",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be contained in the list",
                        placeholder="Enter any value to search for"
                    ),
                    OperatorArg(
                        "occurrences",
                        "number",
                        "Number of occurrences that must be present"
                    )
                ]
            ),
            "contains_any_of": OperatorDef(
                "contains any of",
                [OperatorArg("values", "list", "List of values that might be contained in the list")]
            ),
            "contains_any_of_case_insensitive": OperatorDef(
                "contains any of (case-insensitive)",
                [
                    OperatorArg(
                        "values",
                        "list",
                        "List of values that might be contained in the list (case-insensitive for strings)"
                    )
                ]
            ),
            "contains_none_of": OperatorDef(
                "contains none of",
                [OperatorArg("values", "list", "List of values that must not be contained in the list")]
            ),
            "contains_none_of_case_insensitive": OperatorDef(
                "contains none of (case-insensitive)",
                [
                    OperatorArg(
                        "values",
                        "list",
                        "List of values that must not be contained in the list (case-insensitive for strings)"
                    )
                ]
            ),
            "does_not_contain": OperatorDef(
                "does not contain",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must not be contained in the list",
                        placeholder="Enter any value to search for"
                    )
                ]
            ),
            "does_not_contain_case_insensitive": OperatorDef(
                "does not contain (case-insensitive)",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must not be contained in the list (case-insensitive for strings)",
                        placeholder="Enter any value to search for"
                    )
                ]
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
            "contains_numbers_in_range": OperatorDef(
                "contains numbers in range (inclusive)",
                [
                    OperatorArg("min", "number", "Minimum value in the range (inclusive)"),
                    OperatorArg("max", "number", "Maximum value in the range (inclusive)")
                ]
            ),
            "contains_object_with_key_value": OperatorDef(
                "contains object with key & value",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg("value", "generic", "Value that the key must be equal to")
                ]
            ),
            "contains_object_with_key_value_case_insensitive": OperatorDef(
                "contains object with key & value (case-insensitive)",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that the key must be equal to (case-insensitive for strings)"
                    )
                ]
            ),
            "does_not_contain_object_with_key_value": OperatorDef(
                "does not contain object with key & value",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg("value", "generic", "Value that the key must not be equal to")
                ]
            ),
            "does_not_contain_object_with_key_value_case_insensitive": OperatorDef(
                "does not contain object with key & value (case-insensitive)",
                [
                    OperatorArg("key", "string", "Key of any object contained in the list"),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that the key must not be equal to (case-insensitive for strings)"
                    )
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
            "contains_only_objects_with_keys": OperatorDef(
                "contains only objects with keys",
                [
                    OperatorArg(
                        "keys",
                        "list",
                        "List of keys to look for within all objects in the list"
                    )
                ]
            ),
            "does_not_contain_only_objects_with_keys": OperatorDef(
                "does not contain only objects with keys",
                [
                    OperatorArg(
                        "keys",
                        "list",
                        "List of keys to look for within all objects in the list"
                    )
                ]
            ),
            "contains_object_with_data": OperatorDef(
                "contains object with data",
                [
                    OperatorArg(
                        "data",
                        "object",
                        "Data that may be present within any object in the list"
                    )
                ]
            ),
            "contains_all_objects_with_data": OperatorDef(
                "contains all objects with data",
                [
                    OperatorArg(
                        "data",
                        "object",
                        "Data that must be present within all objects in the list"
                    )
                ]
            ),
            "does_not_contain_object_with_data": OperatorDef(
                "does not contain object with data",
                [
                    OperatorArg(
                        "data",
                        "object",
                        "Data that must not be present within any object in the list"
                    )
                ]
            ),
            "contains_all_elements_in_order": OperatorDef(
                "contains all elements in order",
                [
                    OperatorArg(
                        "sublist",
                        "list",
                        "List that must be contained in order within the list"
                    )
                ]
            ),
            "contains_all_elements_in_order_case_insensitive": OperatorDef(
                "contains all elements in order (case-insensitive)",
                [
                    OperatorArg(
                        "sublist",
                        "list",
                        "List that must be contained in order within the list (case-insensitive for strings)"
                    )
                ]
            ),
            "contains_duplicates_of_value": OperatorDef(
                "contains duplicates of value",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must appear more than once in the list"
                    )
                ]
            ),
            "contains_duplicates_of_value_case_insensitive": OperatorDef(
                "contains duplicates of value (case-insensitive)",
                [
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must appear more than once in the list (case-insensitive for strings)"
                    )
                ]
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
            "has_item_at_index": OperatorDef(
                "has item at index",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be at the specified index"
                    )
                ]
            ),
            "has_item_at_index_case_insensitive": OperatorDef(
                "has item at index (case-insensitive)",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must be at the specified index (case-insensitive for strings)"
                    )
                ]
            ),
            "does_not_have_item_at_index": OperatorDef(
                "does not have item at index",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must not be at the specified index"
                    )
                ]
            ),
            "does_not_have_item_at_index_case_insensitive": OperatorDef(
                "does not have item at index (case-insensitive)",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that must not be at the specified index (case-insensitive for strings)"
                    )
                ]
            ),
            "has_object_with_key_value_at_index": OperatorDef(
                "has object with key & value at index",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "key",
                        "string",
                        "Key to check in the object at the specified index"
                    ),
                    OperatorArg("value", "generic", "Value that the key must equal")
                ]
            ),
            "has_object_with_key_value_at_index_case_insensitive": OperatorDef(
                "has object with key & value at index (case-insensitive)",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "key",
                        "string",
                        "Key to check in the object at the specified index"
                    ),
                    OperatorArg(
                        "value",
                        "generic",
                        "Value that the key must equal (case-insensitive for strings)"
                    )
                ]
            ),
            "object_at_index_has_keys": OperatorDef(
                "object at index has keys",
                [
                    OperatorArg(
                        "index",
                        "number",
                        "Index in the list (negative indices count from the end)"
                    ),
                    OperatorArg(
                        "keys",
                        "list",
                        "List of keys that must be present in the object"
                    )
                ]
            ),
            "contains_any_object_with_key": OperatorDef(
                "contains any object with key",
                [OperatorArg("key", "string", "Key that the object must contain")]
            ),
            "is_null": OperatorDef("is null", [], "Check if value is null")
        }

    def contains(self, value: Union[Any, VocabularyValue]) -> tuple:
        return ("contains", [Argument(value)])

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
        return ("contains all of", [Argument(values, VocabularyValueType.LIST)])

    def contains_any(self, values: Union[List[Any], VocabularyValue]) -> tuple:
        return ("contains any of", [Argument(values, VocabularyValueType.LIST)])

    def contains_none(self, values: Union[List[Any], VocabularyValue]) -> tuple:
        return ("contains none of", [Argument(values, VocabularyValueType.LIST)])

    def not_contains(self, value: Union[Any, VocabularyValue]) -> tuple:
        """Check if list does not contain value"""
        return ("does not contain", [Argument(value)])

    def equals(self, other: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list equals another list"""
        return ("is equal to", [Argument(other, VocabularyValueType.LIST)])

    def not_equals(self, other: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list does not equal another list"""
        return ("is not equal to", [Argument(other, VocabularyValueType.LIST)])

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
            Argument(value)
        ])

    def does_not_contain_object_with_key_value(self, key: Union[str, VocabularyValue], value: Union[Any, VocabularyValue]) -> tuple:
        """Check if list does not contain an object with specified key and value"""
        return ("does not contain object with key & value", [
            Argument(key, VocabularyValueType.STRING),
            Argument(value)
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
        return ("is a sublist of", [Argument(superlist, VocabularyValueType.LIST)])

    def is_superlist_of(self, sublist: Union[List[Any], VocabularyValue]) -> tuple:
        """Check if list contains another list as a sublist"""
        return ("is a superlist of", [Argument(sublist, VocabularyValueType.LIST)])

    def contains_case_insensitive(
        self,
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return ("contains (case-insensitive)", [Argument(value)])

    def longer_than_or_equal(
        self,
        length: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "is longer than or equal to",
            [Argument(length, VocabularyValueType.NUMBER)]
        )

    def shorter_than_or_equal(
        self,
        length: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "is shorter than or equal to",
            [Argument(length, VocabularyValueType.NUMBER)]
        )

    def contains_all_case_insensitive(
        self,
        values: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains all of (case-insensitive)",
            [Argument(values, VocabularyValueType.LIST)]
        )

    def contains_n_occurrences_of(
        self,
        value: Union[Any, VocabularyValue],
        occurrences: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "contains N occurrences of",
            [
                Argument(value),
                Argument(occurrences, VocabularyValueType.NUMBER)
            ]
        )

    def contains_at_least_n_occurrences_of(
        self,
        value: Union[Any, VocabularyValue],
        occurrences: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "contains at least N occurrences of",
            [
                Argument(value),
                Argument(occurrences, VocabularyValueType.NUMBER)
            ]
        )

    def contains_at_most_n_occurrences_of(
        self,
        value: Union[Any, VocabularyValue],
        occurrences: Union[int, VocabularyValue]
    ) -> tuple:
        return (
            "contains at most N occurrences of",
            [
                Argument(value),
                Argument(occurrences, VocabularyValueType.NUMBER)
            ]
        )

    def contains_any_case_insensitive(
        self,
        values: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains any of (case-insensitive)",
            [Argument(values, VocabularyValueType.LIST)]
        )

    def contains_none_case_insensitive(
        self,
        values: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains none of (case-insensitive)",
            [Argument(values, VocabularyValueType.LIST)]
        )

    def not_contains_case_insensitive(
        self,
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return ("does not contain (case-insensitive)", [Argument(value)])

    def contains_numbers_in_range(
        self,
        minimum: Union[int, float, VocabularyValue],
        maximum: Union[int, float, VocabularyValue]
    ) -> tuple:
        return (
            "contains numbers in range (inclusive)",
            [
                Argument(minimum, VocabularyValueType.NUMBER),
                Argument(maximum, VocabularyValueType.NUMBER)
            ]
        )

    def contains_object_with_key_value_case_insensitive(
        self,
        key: Union[str, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "contains object with key & value (case-insensitive)",
            [
                Argument(key, VocabularyValueType.STRING),
                Argument(value)
            ]
        )

    def does_not_contain_object_with_key_value_case_insensitive(
        self,
        key: Union[str, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "does not contain object with key & value (case-insensitive)",
            [
                Argument(key, VocabularyValueType.STRING),
                Argument(value)
            ]
        )

    def contains_only_objects_with_keys(
        self,
        keys: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains only objects with keys",
            [Argument(keys, VocabularyValueType.LIST)]
        )

    def does_not_contain_only_objects_with_keys(
        self,
        keys: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "does not contain only objects with keys",
            [Argument(keys, VocabularyValueType.LIST)]
        )

    def contains_object_with_data(
        self,
        data: Union[dict, VocabularyValue]
    ) -> tuple:
        return (
            "contains object with data",
            [Argument(data, VocabularyValueType.OBJECT)]
        )

    def contains_all_objects_with_data(
        self,
        data: Union[dict, VocabularyValue]
    ) -> tuple:
        return (
            "contains all objects with data",
            [Argument(data, VocabularyValueType.OBJECT)]
        )

    def does_not_contain_object_with_data(
        self,
        data: Union[dict, VocabularyValue]
    ) -> tuple:
        return (
            "does not contain object with data",
            [Argument(data, VocabularyValueType.OBJECT)]
        )

    def contains_all_elements_in_order(
        self,
        sublist: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains all elements in order",
            [Argument(sublist, VocabularyValueType.LIST)]
        )

    def contains_all_elements_in_order_case_insensitive(
        self,
        sublist: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "contains all elements in order (case-insensitive)",
            [Argument(sublist, VocabularyValueType.LIST)]
        )

    def contains_duplicates_of_value(
        self,
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return ("contains duplicates of value", [Argument(value)])

    def contains_duplicates_of_value_case_insensitive(
        self,
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "contains duplicates of value (case-insensitive)",
            [Argument(value)]
        )

    def has_item_at_index(
        self,
        index: Union[int, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "has item at index",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(value)
            ]
        )

    def has_item_at_index_case_insensitive(
        self,
        index: Union[int, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "has item at index (case-insensitive)",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(value)
            ]
        )

    def does_not_have_item_at_index(
        self,
        index: Union[int, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "does not have item at index",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(value)
            ]
        )

    def does_not_have_item_at_index_case_insensitive(
        self,
        index: Union[int, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "does not have item at index (case-insensitive)",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(value)
            ]
        )

    def has_object_with_key_value_at_index(
        self,
        index: Union[int, VocabularyValue],
        key: Union[str, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "has object with key & value at index",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(key, VocabularyValueType.STRING),
                Argument(value)
            ]
        )

    def has_object_with_key_value_at_index_case_insensitive(
        self,
        index: Union[int, VocabularyValue],
        key: Union[str, VocabularyValue],
        value: Union[Any, VocabularyValue]
    ) -> tuple:
        return (
            "has object with key & value at index (case-insensitive)",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(key, VocabularyValueType.STRING),
                Argument(value)
            ]
        )

    def object_at_index_has_keys(
        self,
        index: Union[int, VocabularyValue],
        keys: Union[List[Any], VocabularyValue]
    ) -> tuple:
        return (
            "object at index has keys",
            [
                Argument(index, VocabularyValueType.NUMBER),
                Argument(keys, VocabularyValueType.LIST)
            ]
        )

    def contains_any_object_with_key(
        self,
        key: Union[str, VocabularyValue]
    ) -> tuple:
        return (
            "contains any object with key",
            [Argument(key, VocabularyValueType.STRING)]
        )

    def is_null(self) -> tuple:
        return ("is null", [])
