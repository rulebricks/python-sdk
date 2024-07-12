from .schema import RuleType, SchemaField, Rule, Condition
from .operators import BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator
from .utils import generate_slug
from typing import List, Dict, Any, Union, Type, Tuple
from datetime import datetime
import json
import uuid
import string
import random
import os
import re
from tabulate import tabulate

class RuleBuilder:
    """
    Main class for building and managing rule sets.
    Provides methods for defining schemas, adding rules, and exporting the rule set.
    """

    def __init__(self):
        """
        Initialize a new RuleBuilder instance.
        Sets up basic metadata and empty containers for conditions and schemas.
        """
        self.id = str(uuid.uuid4())
        self.name = "Untitled Rule"
        self.description = ""
        self.slug = self._generate_slug()
        self.conditions: List[Condition] = []
        self.sample_request = {}
        self.sample_response = {}
        self.request_schema: Dict[str, SchemaField] = {}
        self.response_schema: Dict[str, SchemaField] = {}
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
        self.updated_by = "Forge SDK"

    def _generate_slug(self, length=10):
        """
        Generate a random alphanumeric slug.

        Args:
            length (int): The length of the slug to generate. Defaults to 10.

        Returns:
            str: A random alphanumeric slug.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def set_name(self, name: str):
        """
        Set the name of the rule set and update the 'updated_at' timestamp.

        Args:
            name (str): The new name for the rule set.
        """
        self.name = name
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def set_description(self, description: str):
        """
        Set the description of the rule set and update the 'updated_at' timestamp.

        Args:
            description (str): The new description for the rule set.
        """
        self.description = description
        self.updated_at = datetime.utcnow().isoformat() + "Z"

    def add_condition(self) -> Condition:
        """
        Add a new condition to the rule set.

        Returns:
            Condition: The newly created condition.
        """
        condition = Condition()
        self.conditions.append(condition)
        return condition

    def add_request_field(self, key: str, name: str, field_type: RuleType, description: str = "", default_value: Any = None):
        """
        Add a new field to the request schema.

        Args:
            key (str): The unique identifier for the field.
            name (str): The display name of the field.
            field_type (RuleType): The type of the field.
            description (str, optional): A description of the field. Defaults to "".
            default_value (Any, optional): The default value for the field. Defaults to None.
        """
        self.request_schema[key] = SchemaField(key, name, field_type, description, default_value)
        self._update_sample_request(key, default_value)

    def add_response_field(self, key: str, name: str, field_type: RuleType, description: str = "", default_value: Any = None):
        """
        Add a new field to the response schema.

        Args:
            key (str): The unique identifier for the field.
            name (str): The display name of the field.
            field_type (RuleType): The type of the field.
            description (str, optional): A description of the field. Defaults to "".
            default_value (Any, optional): The default value for the field. Defaults to None.
        """
        self.response_schema[key] = SchemaField(key, name, field_type, description, default_value)
        self._update_sample_response(key, default_value)

    def _update_sample_request(self, key: str, value: Any):
        """
        Update the sample request with a new field, supporting dot notation for nested structures.

        Args:
            key (str): The key of the field to update.
            value (Any): The value to set for the field.
        """
        self._update_nested_dict(self.sample_request, key, value)

    def _update_sample_response(self, key: str, value: Any):
        """
        Update the sample response with a new field, supporting dot notation for nested structures.

        Args:
            key (str): The key of the field to update.
            value (Any): The value to set for the field.
        """
        self._update_nested_dict(self.sample_response, key, value)

    def _update_nested_dict(self, d: Dict[str, Any], key: str, value: Any):
        """
        Update a nested dictionary using dot notation.

        Args:
            d (Dict[str, Any]): The dictionary to update.
            key (str): The key to update, which may contain dots for nested structures.
            value (Any): The value to set.
        """
        keys = key.split('.')
        for k in keys[:-1]:
            d = d.setdefault(k, {})
        d[keys[-1]] = value

    def update_condition(self, condition: Condition, key: str, operator: Union[BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator], *args: Any) -> Rule:
        """
        Add a new rule to a condition.

        Args:
            condition (Condition): The condition to which the rule will be added.
            key (str): The key of the field this rule applies to.
            operator (Union[BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator]): The operator for this rule.
            *args: The arguments for the operator.

        Returns:
            Rule: The newly created rule.

        Raises:
            ValueError: If the field is not in the request schema or if the operator is incompatible with the field type.
        """
        if key not in self.request_schema:
            raise ValueError(f"Field '{key}' is not defined in the request schema")

        schema_field = self.request_schema[key]
        if not self._is_operator_compatible(schema_field.type, operator):
            raise ValueError(f"Operator '{operator.value.name}' is not compatible with field type '{schema_field.type.value}'")

        rule = Rule(key, operator, list(args))
        condition.request[key] = rule
        return rule

    def set_condition_response(self, condition: Condition, key: str, value: Any):
        """
        Set a response value for a condition.

        Args:
            condition (Condition): The condition for which to set the response.
            key (str): The key of the response field.
            value (Any): The value to set for the response field.

        Raises:
            ValueError: If the field is not in the response schema or if the value type is incompatible.
        """
        if key not in self.response_schema:
            raise ValueError(f"Field '{key}' is not defined in the response schema")

        schema_field = self.response_schema[key]
        if not isinstance(value, self._get_python_type(schema_field.type)):
            raise ValueError(f"Value '{value}' is not of type '{schema_field.type.value}'")

        condition.response[key] = {"value": value}

    def _is_operator_compatible(self, field_type: RuleType, operator: Union[BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator]) -> bool:
        """
        Check if an operator is compatible with a field type.

        Args:
            field_type (RuleType): The type of the field.
            operator (Union[BooleanOperator, NumberOperator, StringOperator, DateOperator, ListOperator]): The operator to check.

        Returns:
            bool: True if the operator is compatible with the field type, False otherwise.
        """
        return (
            (field_type == RuleType.BOOLEAN and isinstance(operator, BooleanOperator)) or
            (field_type == RuleType.NUMBER and isinstance(operator, NumberOperator)) or
            (field_type == RuleType.STRING and isinstance(operator, StringOperator)) or
            (field_type == RuleType.DATE and isinstance(operator, DateOperator)) or
            (field_type == RuleType.LIST and isinstance(operator, ListOperator))
        )

    def _get_python_type(self, rule_type: RuleType) -> Any:
        """
        Get the corresponding Python type for a RuleType.

        Args:
            rule_type (RuleType): The RuleType to convert.

        Returns:
            type: The corresponding Python type.
        """
        return {
            RuleType.BOOLEAN: bool,
            RuleType.NUMBER: (int, float),
            RuleType.STRING: str,
            RuleType.DATE: datetime,
            RuleType.LIST: list
        }[rule_type]

    def get_condition(self, idx: int) -> Condition:
        """
        Retrieve a condition by its index.

        Args:
            idx (int): The index of the condition to retrieve.

        Returns:
            Condition: The condition at the specified index.

        Raises:
            IndexError: If the index is out of range.
        """
        try:
            return self.conditions[idx]
        except IndexError:
            raise IndexError(f"Condition index {idx} is out of range. There are {len(self.conditions)} conditions.")

    def delete_condition(self, idx: int) -> None:
        """
        Delete a condition at the specified index.

        Args:
            idx (int): The index of the condition to delete.

        Raises:
            IndexError: If the index is out of range.
        """
        try:
            del self.conditions[idx]
            self.updated_at = datetime.utcnow().isoformat() + "Z"
            print(f"Condition at index {idx} has been deleted. There are now {len(self.conditions)} conditions.")
        except IndexError:
            raise IndexError(f"Condition index {idx} is out of range. There are {len(self.conditions)} conditions.")

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the rule set to a dictionary representation.

        Returns:
            Dict[str, Any]: A dictionary representation of the rule set.

        Raises:
            ValueError: If there are no conditions, request columns, or response columns.
        """
        if not self.conditions:
            raise ValueError("At least one condition is required")
        if not self.request_schema:
            raise ValueError("At least one request column is required")
        if not self.response_schema:
            raise ValueError("At least one response column is required")

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "slug": self.slug,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
            "published": False,
            "publishedAt": None,
            "sampleRequest": self.sample_request,
            "testRequest": self.sample_request,  # Using the same structure as sampleRequest
            "sampleResponse": self.sample_response,
            "requestSchema": [
                {
                    "key": field.key,
                    "name": field.name,
                    "type": field.type.value,
                    "description": field.description,
                    "defaultValue": field.default_value,
                    "show": field.show
                } for field in self.request_schema.values()
            ],
            "responseSchema": [
                {
                    "key": field.key,
                    "name": field.name,
                    "type": field.type.value,
                    "description": field.description,
                    "defaultValue": field.default_value,
                    "show": field.show
                } for field in self.response_schema.values()
            ],
            "conditions": [
                {
                    "request": {
                        key: {
                            "op": rule.operator.value.name,
                            "args": [arg for arg in rule.args[0]]
                        } for key, rule in condition.request.items()
                    },
                    "response": condition.response,
                    "settings": condition.settings
                } for condition in self.conditions
            ],
            "form": {},
            "history": [],
            "settings": {},
            "testSuite": [],
            "groups": {},
            "no_conditions": len(self.conditions)
        }

    def to_json(self) -> str:
        """
        Convert the rule set to a JSON string representation.

        Returns:
            str: A JSON string representation of the rule set.
        """
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_table(self) -> str:
        """
        Generate a tabular representation of the rule set.

        Returns:
            str: A string containing a tabular representation of the rule set.
        """
        headers = list(self.request_schema.keys()) + list(self.response_schema.keys())
        table_data = []

        for condition in self.conditions:
            row = []
            for key in self.request_schema.keys():
                if key in condition.request:
                    rule = condition.request[key]
                    op_name = rule.operator.value.name
                    args_str = ", ".join(map(str, rule.args))
                    row.append(f"{op_name}\n({args_str})")
                else:
                    row.append("-")

            for key in self.response_schema.keys():
                if key in condition.response:
                    row.append(condition.response[key]["value"])
                else:
                    row.append("-")

            table_data.append(row)

        return tabulate(table_data, headers=headers, tablefmt="grid")

    def export(self) -> str:
        """
        Export the rule set to a file.

        The filename is automatically generated based on the rule name,
        with "-Generated.rbx" appended. Any characters in the rule name
        that are not alphanumeric or underscore are replaced with underscores.

        Returns:
            str: The name of the file that was created.

        Raises:
            IOError: If there's an error writing to the file.
        """
        # Convert the rule name to a valid filename
        base_name = re.sub(r'[^\w\-_\. ]', '_', self.name)
        base_name = base_name.replace(' ', '_')
        filename = f"{base_name}-Generated.rbx"

        # Ensure the filename is unique
        counter = 1
        while os.path.exists(filename):
            filename = f"{base_name}-Generated_{counter}.rbx"
            counter += 1

        try:
            with open(filename, 'w') as f:
                json.dump(self.to_dict(), f, indent=2, default=str)
            print(f"Rule has been written to {filename}")
            return filename
        except IOError as e:
            print(f"Error writing to file: {e}")
            raise
