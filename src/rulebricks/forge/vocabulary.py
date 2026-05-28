from .types import VocabularyValueNotFoundError, VocabularyValueType
from typing import Dict, Any, Type, List, Optional
from datetime import datetime

class VocabularyValue:
    """A reference to a vocabulary value in the platform"""
    def __init__(self, id: str, name: str, value_type: VocabularyValueType):
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
    def get_expected_type(value_type: VocabularyValueType) -> Type:
        """Get the Python type that corresponds to a VocabularyValueType"""
        type_mapping = {
            VocabularyValueType.STRING: str,
            VocabularyValueType.NUMBER: (int, float),
            VocabularyValueType.BOOLEAN: bool,
            VocabularyValueType.DATE: datetime,
            VocabularyValueType.LIST: list,
            VocabularyValueType.OBJECT: dict,
            VocabularyValueType.FUNCTION: object
        }
        return type_mapping[value_type]

    def __repr__(self) -> str:
        return f"<{self.name.upper()}>"

class Vocabulary:
    """Static accessor for vocabulary values"""
    _workspace = None
    _cache: Dict[str, VocabularyValue] = {}

    @classmethod
    def configure(cls, workspace) -> None:
        """Configure with workspace client"""
        cls._workspace = workspace
        cls._cache = {}  # Reset cache when reconfiguring

    @classmethod
    def get(cls, name: str) -> VocabularyValue:
        """
        Get a vocabulary value by name

        Args:
            name: The name of the vocabulary value

        Returns:
            VocabularyValue: The vocabulary value reference

        Raises:
            VocabularyValueNotFoundError: If the value doesn't exist
            ValueError: If Vocabulary hasn't been configured

        Example:
            >>> max_deductible = Vocabulary.get("max_deductible")
            >>> print(max_deductible)
            <MAX_DEDUCTIBLE>
        """
        if not cls._workspace:
            raise ValueError("Vocabulary not configured. Call Vocabulary.configure(workspace) first")

        # Check cache first
        if name in cls._cache:
            return cls._cache[name]

        # Use SDK to find value
        values = cls._workspace.values.list()
        value = next((v for v in values if v.name == name), None)

        if not value:
            raise VocabularyValueNotFoundError(f"Vocabulary value '{name}' not found")

        # Convert SDK type to our VocabularyValueType
        try:
            value_type = VocabularyValueType(value.type)
        except (ValueError, AttributeError):
            raise ValueError(f"Invalid type '{value.type}' for vocabulary value '{name}'")

        # Create and cache the vocabulary value
        vocabulary_value = VocabularyValue(value.id, name, value_type)
        cls._cache[name] = vocabulary_value
        return vocabulary_value

    @classmethod
    def set(
        cls,
        vocabulary_values: Optional[Dict] = None,
        user_groups: Optional[List[str]] = None,
        metadata_by_name: Optional[Dict[str, Dict[str, Any]]] = None
    ) -> None:
        """
        Upsert one or more vocabulary values in your Rulebricks workspace using a dictionary.

        Args:
            values: A dictionary of vocabulary values to set containing name-value pairs
            user_groups: A list of user groups to assign to the vocabulary values (optional)
            metadata_by_name: Optional metadata keyed by vocabulary value name

        Returns:
            None

        Raises:
            ValueError: If Vocabulary hasn't been configured

        Example:
            >>> Vocabulary.set({
            ...     "max_deductible": 2000,
            ...     "min_deductible": 500
            ... })
        """
        if not cls._workspace:
            raise ValueError("Vocabulary not configured. Call Vocabulary.configure(workspace) first")

        # Upsert the values dictionary
        request = {
            "values": vocabulary_values or {},
            "user_groups": user_groups or []
        }
        if metadata_by_name is not None:
            request["metadata_by_name"] = metadata_by_name

        cls._workspace.values.update(**request)

    @classmethod
    def clear_cache(cls) -> None:
        """Clear the vocabulary values cache"""
        cls._cache = {}
