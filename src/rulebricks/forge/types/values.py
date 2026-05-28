from enum import Enum

class VocabularyValueType(Enum):
    """Matches the value type strings returned by the generated SDK"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    LIST = "list"
    OBJECT = "object"
    FUNCTION = "function"

class VocabularyValueNotFoundError(Exception):
    """Raised when a vocabulary value cannot be found"""
    pass

class TypeMismatchError(Exception):
    """Raised when a vocabulary value's type doesn't match the expected type"""
    pass
