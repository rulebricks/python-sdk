from typing import Callable, Tuple, List, Union, Any
from datetime import datetime
from .operators import BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator

def boolean_op(op: BooleanOperator) -> Callable[[], Tuple[BooleanOperator, List]]:
    """
    Create a type-safe function for boolean operators.

    Args:
        op (BooleanOperator): The boolean operator to create a function for.

    Returns:
        Callable[[], Tuple[BooleanOperator, List]]: A function that returns the operator and an empty list of arguments.
    """
    def wrapper() -> Tuple[BooleanOperator, List]:
        return op, []
    return wrapper

def number_op(op: NumberOperator) -> Callable[..., Tuple[NumberOperator, List[Union[int, float]]]]:
    """
    Create a type-safe function for number operators.

    Args:
        op (NumberOperator): The number operator to create a function for.

    Returns:
        Callable[..., Tuple[NumberOperator, List[Union[int, float]]]]: A function that returns the operator and a list of numeric arguments.
    """
    def wrapper(*args: Union[int, float]) -> Tuple[NumberOperator, List[Union[int, float]]]:
        return op, list(args)
    return wrapper

def string_op(op: StringOperator) -> Callable[..., Tuple[StringOperator, List[str]]]:
    """
    Create a type-safe function for string operators.

    Args:
        op (StringOperator): The string operator to create a function for.

    Returns:
        Callable[..., Tuple[StringOperator, List[str]]]: A function that returns the operator and a list of string arguments.
    """
    def wrapper(*args: str) -> Tuple[StringOperator, List[str]]:
        return op, list(args)
    return wrapper

def date_op(op: DateOperator) -> Callable[..., Tuple[DateOperator, List[Union[datetime, str]]]]:
    """
    Create a type-safe function for date operators.

    Args:
        op (DateOperator): The date operator to create a function for.

    Returns:
        Callable[..., Tuple[DateOperator, List[Union[datetime, str]]]]: A function that returns the operator and a list of date arguments.
    """
    def wrapper(*args: Union[datetime, str]) -> Tuple[DateOperator, List[Union[datetime, str]]]:
        return op, list(args)
    return wrapper

def list_op(op: ListOperator) -> Callable[..., Tuple[ListOperator, List[Any]]]:
    """
    Create a type-safe function for list operators.

    Args:
        op (ListOperator): The list operator to create a function for.

    Returns:
        Callable[..., Tuple[ListOperator, List[Any]]]: A function that returns the operator and a list of arguments.
    """
    def wrapper(*args: Any) -> Tuple[ListOperator, List[Any]]:
        return op, list(args)
    return wrapper
