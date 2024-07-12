from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
from .operators import BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator

class RuleType(Enum):
    """
    Enumeration of supported rule types.
    These types define the kind of data a rule can operate on.
    """
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    DATE = "date"
    LIST = "list"

@dataclass
class SchemaField:
    """
    Represents a field in the request or response schema.
    """
    key: str
    name: str
    type: RuleType
    description: str = ""
    default_value: Any = None
    show: bool = True

@dataclass
class Rule:
    """
    Represents a single rule with its key, operator, and arguments.
    """
    key: str
    operator: Union[BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator]
    args: List[Any] = field(default_factory=list)

@dataclass
class Condition:
    """
    Represents a condition with request rules, response values, and settings.
    """
    request: Dict[str, Rule] = field(default_factory=dict)
    response: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    settings: Dict[str, Any] = field(default_factory=lambda: {"enabled": True, "groupId": None, "priority": 0, "schedule": []})
