from .types import DynamicValueNotFoundError, DynamicValueType
from typing import Dict, Any, Type, List
from datetime import datetime

class DynamicValue:
    """A reference to a dynamic value in the platform"""
    def __init__(self, id: str, name: str, value_type: DynamicValueType):
        self.id = id
        self.name = name
        self.value_type = value_type
        self._rb_type = "globalValue"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "$rb": self._rb_type,
            "name": self.name
        }

    @staticmethod
    def get_expected_type(value_type: DynamicValueType) -> Type:
        """Get the Python type that corresponds to a DynamicValueType"""
        type_mapping = {
            DynamicValueType.STRING: str,
            DynamicValueType.NUMBER: (int, float),
            DynamicValueType.BOOLEAN: bool,
            DynamicValueType.DATE: datetime,
            DynamicValueType.LIST: list,
            DynamicValueType.OBJECT: dict
        }
        return type_mapping[value_type]

    def __repr__(self) -> str:
        return f"<{self.name.upper()}>"

class DynamicValues:
    """Static accessor for dynamic values"""
    _workspace = None
    _cache: Dict[str, DynamicValue] = {}

    @classmethod
    def configure(cls, workspace) -> None:
        """Configure with workspace client"""
        cls._workspace = workspace
        cls._cache = {}  # Reset cache when reconfiguring

    @classmethod
    def get(cls, name: str) -> DynamicValue:
        """
        Get a dynamic value by name

        Args:
            name: The name of the dynamic value

        Returns:
            DynamicValue: The dynamic value reference

        Raises:
            DynamicValueNotFoundError: If the value doesn't exist
            ValueError: If DynamicValues hasn't been configured

        Example:
            >>> max_deductible = DynamicValues.get("max_deductible")
            >>> print(max_deductible)
            <MAX_DEDUCTIBLE>
        """
        if not cls._workspace:
            raise ValueError("DynamicValues not configured. Call DynamicValues.configure(workspace) first")

        # Check cache first
        if name in cls._cache:
            return cls._cache[name]

        # Use SDK to find value
        values = cls._workspace.values.list()
        value = next((v for v in values if v.name == name), None)

        if not value:
            raise DynamicValueNotFoundError(f"Dynamic value '{name}' not found")

        # Convert SDK type to our DynamicValueType
        try:
            value_type = DynamicValueType(value.type)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid type '{value.type}' for dynamic value '{name}'")

        # Create and cache the dynamic value
        dynamic_value = DynamicValue(value.id, name, value_type)
        cls._cache[name] = dynamic_value
        return dynamic_value

    @classmethod
    def set(cls, dynamic_values: Dict = {}, access_groups: List[str] = []) -> None:
        """
        Upsert one or more dynamic values in your Rulebricks workspace using a dictionary.

        Args:
            values: A dictionary of dynamic values to set containing name-value pairs
            access_groups: A list of access groups to assign to the dynamic values (optional)

        Returns:
            None

        Raises:
            ValueError: If DynamicValues hasn't been configured

        Example:
            >>> DynamicValues.set({
            ...     "max_deductible": 2000,
            ...     "min_deductible": 500
            ... })
        """
        if not cls._workspace:
            raise ValueError("DynamicValues not configured. Call DynamicValues.configure(workspace) first")

        # Upsert the values dictionary
        cls._workspace.values.update(
            request={"values": dynamic_values, "access_groups": access_groups}
        )

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the dynamic values cache"""
        cls._cache = {}
