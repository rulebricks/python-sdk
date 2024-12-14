from enum import Enum
from typing import Any, List, Optional, Dict, Callable
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

class RuleType(Enum):
    """Supported rule types"""
    BOOLEAN = "boolean"
    NUMBER = "number"
    STRING = "string"
    DATE = "date"
    LIST = "list"
