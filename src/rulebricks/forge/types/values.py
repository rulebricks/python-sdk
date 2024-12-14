from enum import Enum

class DynamicValueType(Enum):
    """Matches the SDK's ListDynamicValuesResponseItemType"""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    DATE = "date"
    LIST = "list"
    OBJECT = "object"

class DynamicValueNotFoundError(Exception):
    """Raised when a dynamic value cannot be found"""
    pass

class TypeMismatchError(Exception):
    """Raised when a dynamic value's type doesn't match the expected type"""
    pass
