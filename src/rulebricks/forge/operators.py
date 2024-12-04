from enum import Enum
from typing import Any, Union, List, Optional, Dict, Callable
from datetime import datetime
from dataclasses import dataclass, field

@dataclass
class OperatorArg:
    """Defines an argument for an operator"""
    name: str
    type: str
    description: str
    placeholder: Optional[str] = None
    validate: Optional[Callable] = None
    default: Any = None

@dataclass
class OperatorDef:
    """Defines an operator including its arguments and validation"""
    name: str
    args: List[OperatorArg]
    description: Optional[str] = None
    validate: Optional[Callable] = None
    skip_typecheck: bool = False

@dataclass
class Field:
    """Base class for field definitions"""
    name: str
    description: str = ""
    default: Any = None
    operators: Dict[str, OperatorDef] = field(default_factory=dict)

class BooleanField(Field):
    """Valid boolean comparisons/operations in Rulebrickss"""

    def __init__(self, name: str, description: str = "", default: bool = False):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef(
                "any",
                [],
                "Match any boolean value",
                skip_typecheck=True
            ),
            "is_true": OperatorDef(
                "is true",
                [],
                "Check if value is true"
            ),
            "is_false": OperatorDef(
                "is false",
                [],
                "Check if value is false"
            )
        }

    def equals(self, value: bool):
        """Check if value equals the given boolean"""
        op_name = "is true" if value else "is false"
        return (op_name, [])

    def any(self):
        """Match any boolean value"""
        return ("any", [])

class NumberField(Field):
    """Valid number comparisons/operations in Rulebricks"""

    def __init__(self, name: str, description: str = "", default: Union[int, float] = 0):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef(
                "any",
                [],
                "Match any numeric value",
                skip_typecheck=True
            ),
            "equals": OperatorDef(
                "equals",
                [OperatorArg(
                    name="value",
                    type="number",
                    description="Number that value must equal"
                )]
            ),
            "does_not_equal": OperatorDef(
                "does not equal",
                [OperatorArg(
                    name="value",
                    type="number",
                    description="Number that value must not equal"
                )]
            ),
            "greater_than": OperatorDef(
                "greater than",
                [OperatorArg(
                    name="bound",
                    type="number",
                    description="Number that value must be greater than"
                )]
            ),
            "less_than": OperatorDef(
                "less than",
                [OperatorArg(
                    name="bound",
                    type="number",
                    description="Number that value must be less than"
                )]
            ),
            "greater_than_or_equal": OperatorDef(
                "greater than or equal to",
                [OperatorArg(
                    name="bound",
                    type="number",
                    description="Number that value must be greater than or equal to"
                )]
            ),
            "less_than_or_equal": OperatorDef(
                "less than or equal to",
                [OperatorArg(
                    name="bound",
                    type="number",
                    description="Number that value must be less than or equal to"
                )]
            ),
            "between": OperatorDef(
                "between",
                [
                    OperatorArg(
                        name="start",
                        type="number",
                        description="Number that value must be greater than or equal to",
                        placeholder="Start"
                    ),
                    OperatorArg(
                        name="end",
                        type="number",
                        description="Number that value must be less than or equal to",
                        placeholder="End"
                    )
                ],
                validate=lambda args: args[0] < args[1]
            ),
            "not_between": OperatorDef(
                "not between",
                [
                    OperatorArg(
                        name="start",
                        type="number",
                        description="Number that value must be less than",
                        placeholder="Start"
                    ),
                    OperatorArg(
                        name="end",
                        type="number",
                        description="Number that value must be greater than",
                        placeholder="End"
                    )
                ],
                validate=lambda args: args[0] < args[1]
            ),
            "is_even": OperatorDef(
                "is even",
                [],
                "Check if value is even"
            ),
            "is_odd": OperatorDef(
                "is odd",
                [],
                "Check if value is odd"
            ),
            "is_positive": OperatorDef(
                "is positive",
                [],
                "Check if value is greater than zero"
            ),
            "is_negative": OperatorDef(
                "is negative",
                [],
                "Check if value is less than zero"
            ),
            "is_zero": OperatorDef(
                "is zero",
                [],
                "Check if value equals zero"
            ),
            "is_not_zero": OperatorDef(
                "is not zero",
                [],
                "Check if value does not equal zero"
            ),
            "is_multiple_of": OperatorDef(
                "is a multiple of",
                [OperatorArg(
                    name="multiple",
                    type="number",
                    description="Number that value must be a multiple of"
                )]
            ),
            "is_not_multiple_of": OperatorDef(
                "is not a multiple of",
                [OperatorArg(
                    name="multiple",
                    type="number",
                    description="Number that value must not be a multiple of"
                )]
            ),
            "is_power_of": OperatorDef(
                "is a power of",
                [OperatorArg(
                    name="base",
                    type="number",
                    description="The base number"
                )],
                validate=lambda args: args[0] > 0
            )
        }

    def equals(self, value: Union[int, float]):
        """Number that value must equal"""
        return ("equals", [value])

    def not_equals(self, value: Union[int, float]):
        """Number that value must not equal"""
        return ("does not equal", [value])

    def greater_than(self, value: Union[int, float]):
        """Number that value must be greater than"""
        return ("greater than", [value])

    def less_than(self, value: Union[int, float]):
        """Number that value must be less than"""
        return ("less than", [value])

    def greater_than_or_equal(self, value: Union[int, float]):
        """Number that value must be greater than or equal to"""
        return ("greater than or equal to", [value])

    def less_than_or_equal(self, value: Union[int, float]):
        """Number that value must be less than or equal to"""
        return ("less than or equal to", [value])

    def between(self, start: Union[int, float], end: Union[int, float]):
        """Number must be between start and end (inclusive)"""
        op = self.operators["between"]
        if op.validate and not op.validate([start, end]):
            raise ValueError(f"Invalid range for between: start ({start}) must be less than end ({end})")
        return (op.name, [start, end])

    def not_between(self, start: Union[int, float], end: Union[int, float]):
        """Number must not be between start and end"""
        op = self.operators["not_between"]
        if op.validate and not op.validate([start, end]):
            raise ValueError(f"Invalid range for not between: start ({start}) must be less than end ({end})")
        return (op.name, [start, end])

    def is_even(self):
        """Check if value is even"""
        return ("is even", [])

    def is_odd(self):
        """Check if value is odd"""
        return ("is odd", [])

    def is_positive(self):
        """Check if value is greater than zero"""
        return ("is positive", [])

    def is_negative(self):
        """Check if value is less than zero"""
        return ("is negative", [])

    def is_zero(self):
        """Check if value equals zero"""
        return ("is zero", [])

    def is_not_zero(self):
        """Check if value does not equal zero"""
        return ("is not zero", [])

    def is_multiple_of(self, value: Union[int, float]):
        """Check if value is a multiple of the given number"""
        return ("is a multiple of", [value])

    def is_not_multiple_of(self, value: Union[int, float]):
        """Check if value is not a multiple of the given number"""
        return ("is not a multiple of", [value])

    def is_power_of(self, base: Union[int, float]):
        """Check if value is a power of the given base"""
        op = self.operators["is_power_of"]
        if op.validate and not op.validate([base]):
            raise ValueError(f"Invalid base for is power of: {base}. Base must be positive.")
        return (op.name, [base])

class StringField(Field):
    """Valid text comparisons/operations in Rulebricks"""

    def __init__(self, name: str, description: str = "", default: str = ""):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef(
                "any",
                [],
                "Match any string value",
                skip_typecheck=True
            ),
            "contains": OperatorDef(
                "contains",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value to search for within the string",
                    validate=lambda x: len(x) > 0
                )]
            ),
            "does_not_contain": OperatorDef(
                "does not contain",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value to search for within the string",
                    validate=lambda x: len(x) > 0
                )]
            ),
            "equals": OperatorDef(
                "equals",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value to compare against"
                )]
            ),
            "does_not_equal": OperatorDef(
                "does not equal",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value to compare against"
                )]
            ),
            "is_empty": OperatorDef(
                "is empty",
                [],
                "Check if string is empty"
            ),
            "is_not_empty": OperatorDef(
                "is not empty",
                [],
                "Check if string is not empty"
            ),
            "starts_with": OperatorDef(
                "starts with",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value the string should start with",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "ends_with": OperatorDef(
                "ends with",
                [OperatorArg(
                    name="value",
                    type="string",
                    description="The value the string should end with",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "is_included_in": OperatorDef(
                "is included in",
                [OperatorArg(
                    name="value",
                    type="list",
                    description="A list of values the string should be in",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "is_not_included_in": OperatorDef(
                "is not included in",
                [OperatorArg(
                    name="value",
                    type="list",
                    description="A list of values the string should not be in",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "contains_any_of": OperatorDef(
                "contains any of",
                [OperatorArg(
                    name="value",
                    type="list",
                    description="A list of values the string should contain at least one of",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "does_not_contain_any_of": OperatorDef(
                "does not contain any of",
                [OperatorArg(
                    name="value",
                    type="list",
                    description="A list of values the string should not contain",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "matches_regex": OperatorDef(
                "matches RegEx",
                [OperatorArg(
                    name="regex",
                    type="string",
                    description="The regex the string should match",
                    placeholder="^[a-z]+$",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "does_not_match_regex": OperatorDef(
                "does not match RegEx",
                [OperatorArg(
                    name="regex",
                    type="string",
                    description="The regex the string should not match",
                    placeholder="^[a-z]+$",
                    validate=lambda v: len(v) > 0
                )]
            ),
            "is_valid_email": OperatorDef(
                "is a valid email address",
                [],
                "Check if string is a valid email address"
            ),
            "is_not_valid_email": OperatorDef(
                "is not a valid email address",
                [],
                "Check if string is not a valid email address"
            ),
            "is_valid_url": OperatorDef(
                "is a valid URL",
                [],
                "Check if string is a valid URL"
            ),
            "is_not_valid_url": OperatorDef(
                "is not a valid URL",
                [],
                "Check if string is not a valid URL"
            ),
            "is_valid_ip": OperatorDef(
                "is a valid IP address",
                [],
                "Check if string is a valid IP address"
            ),
            "is_not_valid_ip": OperatorDef(
                "is not a valid IP address",
                [],
                "Check if string is not a valid IP address"
            ),
            "is_uppercase": OperatorDef(
                "is uppercase",
                [],
                "Check if string is all uppercase"
            ),
            "is_lowercase": OperatorDef(
                "is lowercase",
                [],
                "Check if string is all lowercase"
            ),
            "is_numeric": OperatorDef(
                "is numeric",
                [],
                "Check if string contains only numeric characters"
            ),
            "contains_only_digits": OperatorDef(
                "contains only digits",
                [],
                "Check if string contains only digits"
            ),
            "contains_only_letters": OperatorDef(
                "contains only letters",
                [],
                "Check if string contains only letters"
            ),
            "contains_only_digits_and_letters": OperatorDef(
                "contains only digits and letters",
                [],
                "Check if string contains only digits and letters"
            )
        }

    def contains(self, value: str):
        """Check if string contains the given value"""
        op = self.operators["contains"]
        if op.args[0].validate and not op.args[0].validate(value):
            raise ValueError(f"Invalid value for contains: {value}")
        return (op.name, [value])

    def not_contains(self, value: str):
        """Check if string does not contain the given value"""
        op = self.operators["does_not_contain"]
        if op.args[0].validate and not op.args[0].validate(value):
            raise ValueError(f"Invalid value for does not contain: {value}")
        return (op.name, [value])

    def equals(self, value: str):
        """Check if string equals the given value"""
        return ("equals", [value])

    def not_equals(self, value: str):
        """Check if string does not equal the given value"""
        return ("does not equal", [value])

    def is_empty(self):
        """Check if string is empty"""
        return ("is empty", [])

    def is_not_empty(self):
        """Check if string is not empty"""
        return ("is not empty", [])

    def starts_with(self, value: str):
        """Check if string starts with the given value"""
        op = self.operators["starts_with"]
        if op.args[0].validate and not op.args[0].validate(value):
            raise ValueError(f"Invalid value for starts with: {value}")
        return (op.name, [value])

    def ends_with(self, value: str):
        """Check if string ends with the given value"""
        op = self.operators["ends_with"]
        if op.args[0].validate and not op.args[0].validate(value):
            raise ValueError(f"Invalid value for ends with: {value}")
        return (op.name, [value])

    def is_included_in(self, values: List[str]):
        """Check if string is included in the given list"""
        op = self.operators["is_included_in"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")
        return (op.name, [values])

    def is_not_included_in(self, values: List[str]):
        """Check if string is not included in the given list"""
        op = self.operators["is_not_included_in"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")
        return (op.name, [values])

    def contains_any_of(self, values: List[str]):
        """Check if string contains any of the given values"""
        op = self.operators["contains_any_of"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")
        return (op.name, [values])

    def not_contains_any_of(self, values: List[str]):
        """Check if string does not contain any of the given values"""
        op = self.operators["does_not_contain_any_of"]
        if op.args[0].validate and not op.args[0].validate(values):
            raise ValueError("List must not be empty")
        return (op.name, [values])

    def matches_regex(self, pattern: str):
        """Check if string matches the given regex pattern"""
        op = self.operators["matches_regex"]
        if op.args[0].validate and not op.args[0].validate(pattern):
            raise ValueError(f"Invalid regex pattern: {pattern}")
        return (op.name, [pattern])

    def not_matches_regex(self, pattern: str):
        """Check if string does not match the given regex pattern"""
        op = self.operators["does_not_match_regex"]
        if op.args[0].validate and not op.args[0].validate(pattern):
            raise ValueError(f"Invalid regex pattern: {pattern}")
        return (op.name, [pattern])

    def is_email(self):
        """Check if string is a valid email address"""
        return ("is a valid email address", [])

    def is_not_email(self):
        """Check if string is not a valid email address"""
        return ("is not a valid email address", [])

    def is_url(self):
        """Check if string is a valid URL"""
        return ("is a valid URL", [])

    def is_not_url(self):
        """Check if string is not a valid URL"""
        return ("is not a valid URL", [])

    def is_ip(self):
        """Check if string is a valid IP address"""
        return ("is a valid IP address", [])

    def is_not_ip(self):
        """Check if string is not a valid IP address"""
        return ("is not a valid IP address", [])

    def is_uppercase(self):
        """Check if string is all uppercase"""
        return ("is uppercase", [])

    def is_lowercase(self):
        """Check if string is all lowercase"""
        return ("is lowercase", [])

    def is_numeric(self):
        """Check if string contains only numeric characters"""
        return ("is numeric", [])

    def contains_only_digits(self):
        """Check if string contains only digits"""
        return ("contains only digits", [])

    def contains_only_letters(self):
        """Check if string contains only letters"""
        return ("contains only letters", [])

    def contains_only_digits_and_letters(self):
        """Check if string contains only digits and letters"""
        return ("contains only digits and letters", [])

class DateField(Field):
    """Valid date comparisons/operations in Rulebricks"""

    def __init__(self, name: str, description: str = "", default: Optional[datetime] = None):
        super().__init__(name, description, default)
        self.operators = {
            "any": OperatorDef(
                "any",
                [],
                "Match any date value",
                skip_typecheck=True
            ),
            "is_past": OperatorDef(
                "is in the past",
                [],
                "Date is in the past"
            ),
            "is_future": OperatorDef(
                "is in the future",
                [],
                "Date is in the future"
            ),
            "days_ago": OperatorDef(
                "days ago",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days ago that the date is equal to"
                )]
            ),
            "less_than_days_ago": OperatorDef(
                "is less than N days ago",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days ago that the date is less than or equal to"
                )]
            ),
            "more_than_days_ago": OperatorDef(
                "is more than N days ago",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days ago that the date is more than or equal to"
                )]
            ),
            "days_from_now": OperatorDef(
                "days from now",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days from now that the date is equal to"
                )]
            ),
            "less_than_days_from_now": OperatorDef(
                "is less than N days from now",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days from now that the date is less than or equal to"
                )]
            ),
            "more_than_days_from_now": OperatorDef(
                "is more than N days from now",
                [OperatorArg(
                    name="days",
                    type="number",
                    description="Number of days from now that the date is more than or equal to"
                )]
            ),
            "is_today": OperatorDef(
                "is today",
                [],
                "Date is today"
            ),
            "is_this_week": OperatorDef(
                "is this week",
                [],
                "Date is in the current week"
            ),
            "is_this_month": OperatorDef(
                "is this month",
                [],
                "Date is in the current month"
            ),
            "is_this_year": OperatorDef(
                "is this year",
                [],
                "Date is in the current year"
            ),
            "is_next_week": OperatorDef(
                "is next week",
                [],
                "Date is in the next week"
            ),
            "is_next_month": OperatorDef(
                "is next month",
                [],
                "Date is in the next month"
            ),
            "is_next_year": OperatorDef(
                "is next year",
                [],
                "Date is in the next year"
            ),
            "is_last_week": OperatorDef(
                "is last week",
                [],
                "Date is in the previous week"
            ),
            "is_last_month": OperatorDef(
                "is last month",
                [],
                "Date is in the previous month"
            ),
            "is_last_year": OperatorDef(
                "is last year",
                [],
                "Date is in the previous year"
            ),
            "after": OperatorDef(
                "after",
                [OperatorArg(
                    name="date",
                    type="date",
                    description="Date that value must be after"
                )]
            ),
            "on_or_after": OperatorDef(
                "on or after",
                [OperatorArg(
                    name="date",
                    type="date",
                    description="Date that value must be on or after"
                )]
            ),
            "before": OperatorDef(
                "before",
                [OperatorArg(
                    name="date",
                    type="date",
                    description="Date that value must be before"
                )]
            ),
            "on_or_before": OperatorDef(
                "on or before",
                [OperatorArg(
                    name="date",
                    type="date",
                    description="Date that value must be on or before"
                )]
            ),
            "between": OperatorDef(
                "between",
                [
                    OperatorArg(
                        name="start",
                        type="date",
                        description="Date that value must be after",
                        placeholder="From"
                    ),
                    OperatorArg(
                        name="end",
                        type="date",
                        description="Date that value must be before",
                        placeholder="To"
                    )
                ]
            ),
            "not_between": OperatorDef(
                "not between",
                [
                    OperatorArg(
                        name="start",
                        type="date",
                        description="Date that value must be before",
                        placeholder="From"
                    ),
                    OperatorArg(
                        name="end",
                        type="date",
                        description="Date that value must be after",
                        placeholder="To"
                    )
                ]
            )
        }

    def is_past(self):
        """Check if date is in the past"""
        return ("is in the past", [])

    def is_future(self):
        """Check if date is in the future"""
        return ("is in the future", [])

    def days_ago(self, days: int):
        """Check if date is exactly N days ago"""
        return ("days ago", [days])

    def less_than_days_ago(self, days: int):
        """Check if date is less than N days ago"""
        return ("is less than N days ago", [days])

    def more_than_days_ago(self, days: int):
        """Check if date is more than N days ago"""
        return ("is more than N days ago", [days])

    def days_from_now(self, days: int):
        """Check if date is exactly N days from now"""
        return ("days from now", [days])

    def less_than_days_from_now(self, days: int):
        """Check if date is less than N days from now"""
        return ("is less than N days from now", [days])

    def more_than_days_from_now(self, days: int):
        """Check if date is more than N days from now"""
        return ("is more than N days from now", [days])

    def is_today(self):
        """Check if date is today"""
        return ("is today", [])

    def is_this_week(self):
        """Check if date is in the current week"""
        return ("is this week", [])

    def is_this_month(self):
        """Check if date is in the current month"""
        return ("is this month", [])

    def is_this_year(self):
        """Check if date is in the current year"""
        return ("is this year", [])

    def is_next_week(self):
        """Check if date is in the next week"""
        return ("is next week", [])

    def is_next_month(self):
        """Check if date is in the next month"""
        return ("is next month", [])

    def is_next_year(self):
        """Check if date is in the next year"""
        return ("is next year", [])

    def is_last_week(self):
        """Check if date is in the previous week"""
        return ("is last week", [])

    def is_last_month(self):
        """Check if date is in the previous month"""
        return ("is last month", [])

    def is_last_year(self):
        """Check if date is in the previous year"""
        return ("is last year", [])

    def after(self, date: Union[datetime, str]):
        """Check if date is after the given date"""
        return ("after", [date])

    def on_or_after(self, date: Union[datetime, str]):
        """Check if date is on or after the given date"""
        return ("on or after", [date])

    def before(self, date: Union[datetime, str]):
        """Check if date is before the given date"""
        return ("before", [date])

    def on_or_before(self, date: Union[datetime, str]):
        """Check if date is on or before the given date"""
        return ("on or before", [date])

    def between(self, start: Union[datetime, str], end: Union[datetime, str]):
        """Check if date is between start and end dates"""
        return ("between", [start, end])

    def not_between(self, start: Union[datetime, str], end: Union[datetime, str]):
        """Check if date is not between start and end dates"""
        return ("not between", [start, end])

class ListField(Field):
    """Valid list comparisons/operations in Rulebricks"""

    def __init__(self, name: str, description: str = "", default: Optional[List] = None):
        super().__init__(name, description, default or [])
        self.operators = {
            "any": OperatorDef(
                "any",
                [],
                "Match any list value",
                skip_typecheck=True
            ),
            "contains": OperatorDef(
                "contains",
                [OperatorArg(
                    name="value",
                    type="generic",
                    description="Value that must be contained in the list",
                    placeholder="Enter any value to search for"
                )]
            ),
            "is_empty": OperatorDef(
                "is empty",
                [],
                "Check if list is empty"
            ),
            "is_not_empty": OperatorDef(
                "is not empty",
                [],
                "Check if list is not empty"
            ),
            "is_of_length": OperatorDef(
                "is of length",
                [OperatorArg(
                    name="length",
                    type="number",
                    description="Length that the list must be"
                )]
            ),
            "is_not_of_length": OperatorDef(
                "is not of length",
                [OperatorArg(
                    name="length",
                    type="number",
                    description="Length that the list must not be"
                )]
            ),
            "is_longer_than": OperatorDef(
                "is longer than",
                [OperatorArg(
                    name="length",
                    type="number",
                    description="Length that the list must be longer than"
                )]
            ),
            "is_shorter_than": OperatorDef(
                "is shorter than",
                [OperatorArg(
                    name="length",
                    type="number",
                    description="Length that the list must be shorter than"
                )]
            ),
            "contains_all_of": OperatorDef(
                "contains all of",
                [OperatorArg(
                    name="values",
                    type="list",
                    description="List of values that must be contained in the list"
                )]
            ),
            "contains_any_of": OperatorDef(
                "contains any of",
                [OperatorArg(
                    name="values",
                    type="list",
                    description="List of values that might be contained in the list"
                )]
            ),
            "contains_none_of": OperatorDef(
                "contains none of",
                [OperatorArg(
                    name="values",
                    type="list",
                    description="List of values that must not be contained in the list"
                )]
            ),
            "does_not_contain": OperatorDef(
                "does not contain",
                [OperatorArg(
                    name="value",
                    type="generic",
                    description="Value that must not be contained in the list"
                )]
            ),
            "is_equal_to": OperatorDef(
                "is equal to",
                [OperatorArg(
                    name="list",
                    type="list",
                    description="Value that the list must be equal to"
                )]
            ),
            "is_not_equal_to": OperatorDef(
                "is not equal to",
                [OperatorArg(
                    name="list",
                    type="list",
                    description="Value that the list must not be equal to"
                )]
            ),
            "contains_duplicates": OperatorDef(
                "contains duplicates",
                [],
                "Check if list contains duplicate values"
            ),
            "does_not_contain_duplicates": OperatorDef(
                "does not contain duplicates",
                [],
                "Check if list does not contain duplicate values"
            ),
            "contains_object_with_key_value": OperatorDef(
                "contains object with key & value",
                [
                    OperatorArg(
                        name="key",
                        type="string",
                        description="Key of any object contained in the list"
                    ),
                    OperatorArg(
                        name="value",
                        type="generic",
                        description="Value that the key must be equal to"
                    )
                ]
            ),
            "has_unique_elements": OperatorDef(
                "has unique elements",
                [],
                "Check if all elements in the list are unique"
            ),
            "is_sublist_of": OperatorDef(
                "is a sublist of",
                [OperatorArg(
                    name="superlist",
                    type="list",
                    description="List that must contain this list as a sublist"
                )]
            ),
            "is_superlist_of": OperatorDef(
                "is a superlist of",
                [OperatorArg(
                    name="sublist",
                    type="list",
                    description="List that must be contained as a sublist within this list"
                )]
            )
        }

    def contains(self, value: Any):
        """Check if list contains the given value"""
        return ("contains", [value])

    def is_empty(self):
        """Check if list is empty"""
        return ("is empty", [])

    def is_not_empty(self):
        """Check if list is not empty"""
        return ("is not empty", [])

    def length_equals(self, length: int):
        """Check if list has exact length"""
        return ("is of length", [length])

    def length_not_equals(self, length: int):
        """Check if list does not have exact length"""
        return ("is not of length", [length])

    def longer_than(self, length: int):
        """Check if list is longer than length"""
        return ("is longer than", [length])

    def shorter_than(self, length: int):
        """Check if list is shorter than length"""
        return ("is shorter than", [length])

    def contains_all(self, values: List[Any]):
        """Check if list contains all values"""
        return ("contains all of", [values])

    def contains_any(self, values: List[Any]):
        """Check if list contains any of values"""
        return ("contains any of", [values])

    def contains_none(self, values: List[Any]):
        """Check if list contains none of values"""
        return ("contains none of", [values])

    def not_contains(self, value: Any):
        """Check if list does not contain value"""
        return ("does not contain", [value])

    def equals(self, other: List[Any]):
        """Check if list equals another list"""
        return ("is equal to", [other])

    def not_equals(self, other: List[Any]):
        """Check if list does not equal another list"""
        return ("is not equal to", [other])

    def has_duplicates(self):
        """Check if list has duplicate values"""
        return ("contains duplicates", [])

    def no_duplicates(self):
        """Check if list has no duplicate values"""
        return ("does not contain duplicates", [])

    def contains_object_with_key_value(self, key: str, value: Any):
        """Check if list contains an object with specified key and value"""
        return ("contains object with key & value", [key, value])

    def has_unique_elements(self):
        """Check if all elements in the list are unique"""
        return ("has unique elements", [])

    def is_sublist_of(self, superlist: List[Any]):
        """Check if list is a sublist of another list"""
        return ("is a sublist of", [superlist])

    def is_superlist_of(self, sublist: List[Any]):
        """Check if list contains another list as a sublist"""
        return ("is a superlist of", [sublist])

class RuleType(Enum):
    """Supported rule types"""
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    DATE = "date"
    LIST = "list"
