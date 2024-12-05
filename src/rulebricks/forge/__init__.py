from .operators import BooleanField, NumberField, StringField, DateField, ListField, RuleType
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import json
import uuid
import string
import random
import os
import re

class Rule:
    """Main class for building and managing rules"""

    def __init__(self):
        self.request_fields: Dict[str, Union[BooleanField, NumberField, StringField, DateField, ListField]] = {}
        self.response_fields: Dict[str, Union[BooleanField, NumberField, StringField, DateField, ListField]] = {}
        self.conditions: List[Dict] = []
        self.name: str = "Untitled Rule"
        self.description: str = ""
        self.id: str = str(uuid.uuid4())
        self.created_at: str = datetime.utcnow().isoformat() + "Z"
        self.updated_at: str = self.created_at
        self.updated_by: str = "Rulebricks SDK"
        self.slug: str = self._generate_slug()

    @classmethod
    def from_json(cls, json_str: Union[str, Dict[str, Any]]) -> 'Rule':
        """
        Create a Rule instance from a JSON string or dictionary.

        Args:
            json_str: Either a JSON string or a dictionary containing rule data

        Returns:
            A new Rule instance populated with the data

        Raises:
            ValueError: If the JSON data is invalid or missing required fields
        """
        # Convert string to dict if necessary
        if isinstance(json_str, str):
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid JSON string: {e}")
        else:
            data = json_str

        if not isinstance(data, dict):
            raise ValueError("Input must be a dictionary or JSON object")

        # Create new rule instance
        rule = cls()

        # Set basic attributes
        rule.id = data.get('id', str(uuid.uuid4()))
        rule.name = data.get('name', 'Untitled Rule')
        rule.description = data.get('description', '')
        rule.slug = data.get('slug', rule._generate_slug())
        rule.created_at = data.get('createdAt', datetime.utcnow().isoformat() + "Z")
        rule.updated_at = data.get('updatedAt', rule.created_at)
        rule.updated_by = data.get('updatedBy', 'Rulebricks SDK')

        # Process request schema
        for field in data.get('requestSchema', []):
            try:
                field_type = RuleType(field['type'])
                if field_type == RuleType.BOOLEAN:
                    rule.add_boolean_field(field['key'], field.get('description', ''), field.get('defaultValue', False))
                elif field_type == RuleType.NUMBER:
                    rule.add_number_field(field['key'], field.get('description', ''), field.get('defaultValue', 0))
                elif field_type == RuleType.STRING:
                    rule.add_string_field(field['key'], field.get('description', ''), field.get('defaultValue', ''))
                elif field_type == RuleType.DATE:
                    rule.add_date_field(field['key'], field.get('description', ''), field.get('defaultValue'))
                elif field_type == RuleType.LIST:
                    rule.add_list_field(field['key'], field.get('description', ''), field.get('defaultValue', []))
            except KeyError as e:
                raise ValueError(f"Missing required field in requestSchema: {str(e)}")

        # Process response schema
        for field in data.get('responseSchema', []):
            try:
                field_type = RuleType(field['type'])
                if field_type == RuleType.BOOLEAN:
                    rule.add_boolean_response(field['key'], field.get('description', ''), field.get('defaultValue', False))
                elif field_type == RuleType.NUMBER:
                    rule.add_number_response(field['key'], field.get('description', ''), field.get('defaultValue', 0))
                elif field_type == RuleType.STRING:
                    rule.add_string_response(field['key'], field.get('description', ''), field.get('defaultValue', ''))
                elif field_type == RuleType.DATE:
                    rule.add_date_field(field['key'], field.get('description', ''), field.get('defaultValue'))
                elif field_type == RuleType.LIST:
                    rule.add_list_field(field['key'], field.get('description', ''), field.get('defaultValue', []))
            except KeyError as e:
                raise ValueError(f"Missing required field in responseSchema: {str(e)}")

        # Process conditions
        rule.conditions = data.get('conditions', [])

        return rule

    def _generate_slug(self, length: int = 10) -> str:
        """Generate a random alphanumeric slug"""
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def _get_field_type(self, field: Union[BooleanField, NumberField, StringField, DateField, ListField]) -> RuleType:
        """Get the RuleType for a field"""
        type_mapping = {
            BooleanField: RuleType.BOOLEAN,
            NumberField: RuleType.NUMBER,
            StringField: RuleType.STRING,
            DateField: RuleType.DATE,
            ListField: RuleType.LIST
        }
        return type_mapping[field.__class__]

    def set_name(self, name: str) -> 'Rule':
        """Set the rule name"""
        self.name = name
        return self

    def set_description(self, description: str) -> 'Rule':
        """Set the rule description"""
        self.description = description
        return self

    def add_boolean_field(self, name: str, description: str = "", default: bool = False) -> BooleanField:
        """Add a boolean request field"""
        field = BooleanField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_number_field(self, name: str, description: str = "", default: Union[int, float] = 0) -> NumberField:
        """Add a number request field"""
        field = NumberField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_string_field(self, name: str, description: str = "", default: str = "") -> StringField:
        """Add a string request field"""
        field = StringField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_date_field(self, name: str, description: str = "", default: Optional[datetime] = None) -> DateField:
        """Add a date request field"""
        field = DateField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_list_field(self, name: str, description: str = "", default: Optional[List] = None) -> ListField:
        """Add a list request field"""
        field = ListField(name, description, default or [])
        self.request_fields[name] = field
        return field

    def add_boolean_response(self, name: str, description: str = "", default: bool = False) -> BooleanField:
        """Add a boolean response field"""
        field = BooleanField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_number_response(self, name: str, description: str = "", default: Union[int, float] = 0) -> NumberField:
        """Add a number response field"""
        field = NumberField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_string_response(self, name: str, description: str = "", default: str = "") -> StringField:
        """Add a string response field"""
        field = StringField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_date_response(self, name: str, description: str = "", default: Optional[datetime] = None) -> DateField:
        """Add a date response field"""
        field = DateField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_list_response(self, name: str, description: str = "", default: Optional[List] = None) -> ListField:
        """Add a list response field"""
        field = ListField(name, description, default or [])
        self.response_fields[name] = field
        return field

    def when(self, **conditions) -> 'Condition':
        """Start defining a new condition"""
        return Condition(self, conditions)

    def any(self, **conditions) -> 'Condition':
        """Start defining a new condition with an OR operator"""
        return Condition(self, conditions, settings={ "or": True })

    def to_dict(self) -> Dict[str, Any]:
        """Convert the rule to a dictionary representation"""
        # Use request fields and response fields to generate sampleRequest and sampleResponse json
        sampleRequest = {}
        sampleResponse = {}

        for name, field in self.request_fields.items():
            parts = name.split('.')
            current = sampleRequest
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = field.default

        for name, field in self.response_fields.items():
            parts = name.split('.')
            current = sampleResponse
            for part in parts[:-1]:
                current = current.setdefault(part, {})
            current[parts[-1]] = field.default

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
            "sampleRequest": sampleRequest,
            "sampleResponse": sampleResponse,
            "testRequest": sampleRequest,
            "requestSchema": [
                {
                    "key": name,
                    "name": field.name,
                    "type": self._get_field_type(field).value,
                    "description": field.description,
                    "defaultValue": field.default,
                    "show": True
                }
                for name, field in self.request_fields.items()
            ],
            "responseSchema": [
                {
                    "key": name,
                    "name": field.name,
                    "type": self._get_field_type(field).value,
                    "description": field.description,
                    "defaultValue": field.default,
                    "show": True
                }
                for name, field in self.response_fields.items()
            ],
            "conditions": self.conditions,
            "form": {},
            "history": [],
            "settings": {},
            "testSuite": [],
            "groups": {},
            "no_conditions": len(self.conditions)
        }

    def to_json(self) -> str:
        """Convert the rule to a JSON string"""
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_table(self) -> str:
        """
        Generate a tabular representation of the rule conditions.
        Uses the tabulate library to create a formatted grid view.

        Returns:
            str: A string containing the tabular representation of the rule
        """
        from tabulate import tabulate

        # Get all field names for headers
        headers = list(self.request_fields.keys()) + list(self.response_fields.keys())
        table_data = []

        for condition in self.conditions:
            row = []

            # Add request field values
            for field_name in self.request_fields.keys():
                if field_name in condition["request"]:
                    rule = condition["request"][field_name]
                    op_name = rule["op"]
                    args_str = ", ".join(map(str, rule["args"]))
                    row.append(f"{op_name}\n({args_str})")
                else:
                    row.append("-")

            # Add response field values
            for field_name in self.response_fields.keys():
                if field_name in condition["response"]:
                    row.append(condition["response"][field_name]["value"])
                else:
                    row.append("-")

            table_data.append(row)

        return tabulate(table_data, headers=headers, tablefmt="grid")

    def export(self, directory: Optional[str] = None) -> str:
        """
        Export the rule to a file

        Args:
            directory: Optional directory to save the file in

        Returns:
            The path to the exported file
        """
        base_name = re.sub(r'[^\w\-_\. ]', '_', self.name)
        base_name = base_name.replace(' ', '_')
        filename = f"{base_name}-Generated.rbx"

        if directory:
            os.makedirs(directory, exist_ok=True)
            filename = os.path.join(directory, filename)

        # Ensure filename is unique
        counter = 1
        while os.path.exists(filename):
            name_parts = filename.rsplit('-Generated', 1)
            filename = f"{name_parts[0]}-Generated_{counter}.rbx"
            counter += 1

        with open(filename, 'w') as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

        return filename

class Condition:
    """Helper class for building conditions using the fluent interface"""

    def __init__(self, rule: Rule, conditions: Dict, settings: Dict = {}):
        self.rule = rule
        self.conditions = conditions
        self.responses = {}
        self.settings = {"enabled": True, "groupId": None, "priority": 0, "schedule": []}
        self.settings.update(settings)

    def then(self, **responses) -> Rule:
        """Set the responses for this condition"""
        self.responses = responses
        condition = {
            "request": {},
            "response": {},
            "settings": self.settings
        }

        # Process conditions
        for field_name, (operator, args) in self.conditions.items():
            if field_name not in self.rule.request_fields:
                raise ValueError(f"Field '{field_name}' is not defined in request schema")
            condition["request"][field_name] = {
                "op": operator,
                "args": args
            }

        # Process responses
        for field_name, value in self.responses.items():
            if field_name not in self.rule.response_fields:
                raise ValueError(f"Field '{field_name}' is not defined in response schema")
            condition["response"][field_name] = {"value": value}

        self.rule.conditions.append(condition)
        return self.rule

    def disable(self) -> 'Condition':
        """Disable this condition"""
        self.settings["enabled"] = False
        return self

    def set_priority(self, priority: int) -> 'Condition':
        """Set the priority of this condition"""
        self.settings["priority"] = priority
        return self
