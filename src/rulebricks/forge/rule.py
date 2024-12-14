from .types.operators import RuleType
from .operators import BooleanField, NumberField, StringField, DateField, ListField
from .values import DynamicValue
from typing import Any, Dict, List, Optional, Union, TYPE_CHECKING
from datetime import datetime
import json
import uuid
import string
import random
import os
import re

if TYPE_CHECKING:
    from ..client import RulebricksApi

def process_dynamic_values(arg: Any) -> Any:
    """Process any argument into the correct format for conditions"""
    if isinstance(arg, DynamicValue):
        return arg.to_dict()
    elif isinstance(arg, list):
        return [process_dynamic_values(item) for item in arg]
    elif isinstance(arg, dict):
        return {k: process_dynamic_values(v) for k, v in arg.items()}
    return arg

class Condition:
    """Class for building and modifying conditions"""

    def __init__(
            self,
            rule: 'Rule',
            conditions: Optional[Dict] = None,
            index: Optional[int] = None,
            settings: Optional[Dict] = None
        ):
            self.rule = rule
            self.conditions = conditions if conditions is not None else {}
            self.index = index  # None for new conditions, index for editing existing
            self.responses = {}
            self.settings = {"enabled": True, "groupId": None, "priority": 0, "schedule": []}
            if settings is not None:
                self.settings.update(settings)

    def when(self, **conditions) -> 'Condition':
        """Set or update conditions"""
        for field_name, (operator, args) in conditions.items():
            if field_name not in self.rule.request_fields:
                raise ValueError(f"Field '{field_name}' is not defined in request schema")
            if self.index is not None:  # Editing existing condition
                self.rule.conditions[self.index]["request"][field_name] = {
                    "op": operator,
                    "args": [process_dynamic_values(arg) for arg in args]
                }
            else:  # Creating new condition
                self.conditions[field_name] = (operator, args)
        return self

    def then(self, **responses) -> Union['Rule', 'Condition']:
        """Set or update responses"""
        for field_name, value in responses.items():
            if field_name not in self.rule.response_fields:
                raise ValueError(f"Field '{field_name}' is not defined in response schema")

        if self.index is not None:  # Editing existing condition
            for field_name, value in responses.items():
                self.rule.conditions[self.index]["response"][field_name] = {
                    "value": process_dynamic_values(value)
                }
            return self

        else:  # Creating new condition
            self.responses = responses
            condition = {
                "request": {},
                "response": {},
                "settings": self.settings
            }

            # Process conditions
            for field_name, (operator, args) in self.conditions.items():
                condition["request"][field_name] = {
                    "op": operator,
                    "args": [process_dynamic_values(arg) for arg in args]
                }

            # Process responses
            for field_name, value in self.responses.items():
                condition["response"][field_name] = {
                    "value": process_dynamic_values(value)
                }

            self.rule.conditions.append(condition)
            return self.rule

    def set_priority(self, priority: int) -> 'Condition':
        """Set the condition priority"""
        self.settings["priority"] = priority
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["priority"] = priority
        return self

    def enable(self) -> 'Condition':
        """Enable the condition"""
        self.settings["enabled"] = True
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["enabled"] = True
        return self

    def disable(self) -> 'Condition':
        """Disable the condition"""
        self.settings["enabled"] = False
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["enabled"] = False
        return self

    def delete(self) -> None:
        """Remove this condition from the rule"""
        if self.index is not None:
            self.rule.conditions.pop(self.index)

class RuleTest:
    """
    Rule tests allow users to define test cases for a rule to ensure it behaves as expected.
    """

    def __init__(self):
        self.id = self._generate_id()
        self.name = "Untitled Test"
        self.request = {}
        self.response = {}
        self.critical = False
        self.last_executed = None
        self.test_state = None
        self.error = None
        self.success = None

    def _generate_id(self) -> str:
        return ''.join(random.choices(string.ascii_letters + string.digits, k=21))

    def set_name(self, name: str) -> 'RuleTest':
        """Set the name of the test"""
        self.name = name
        return self

    def expect(self, request: Dict[str, Any], response: Dict[str, Any]) -> 'RuleTest':
        """Set the request and associated expected response payload for this test"""
        self.request = request
        self.response = response
        return self

    def is_critical(self, critical: bool = True) -> 'RuleTest':
        """Set the test as critical or not"""
        self.critical = critical
        return self

    def to_dict(self) -> Dict[str, Any]:
        """Convert the test to a dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "request": self.request,
            "response": self.response,
            "critical": self.critical,
            "lastExecuted": self.last_executed,
            "testState": self.test_state,
            "error": self.error,
            "success": self.success
        }

    @classmethod
    def from_json(cls, json_str: Union[str, Dict[str, Any]]) -> 'RuleTest':
        """
        Create a RuleTest instance from a JSON string or dictionary.

        Args:
            json_str: Either a JSON string or a dictionary containing test data

        Returns:
            A new RuleTest instance populated with the data

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
        test = cls()

        # Set basic attributes
        test.id = data.get('id', test._generate_id())
        test.name = data.get('name', 'Untitled Test')
        test.request = data.get('request', {})
        test.response = data.get('response', {})
        test.critical = data.get('critical', False)
        test.last_executed = data.get('lastExecuted', None)
        test.test_state = data.get('testState', None)
        test.error = data.get('error', None)
        test.success = data.get('success', None)

        return test


class Rule:
    """Main class for building and managing rules"""

    def __init__(self, rulebricks_client: Optional['RulebricksApi'] = None):
        self.workspace = rulebricks_client
        self.request_fields: Dict[str, Union[BooleanField, NumberField, StringField, DateField, ListField]] = {}
        self.response_fields: Dict[str, Union[BooleanField, NumberField, StringField, DateField, ListField]] = {}
        self.test_request = None
        self.conditions: List[Dict] = []
        self.groups: Dict[str, Any] = {}
        self.name: str = "Untitled Rule"
        self.description: str = ""
        self.id: str = str(uuid.uuid4())
        self.created_at: str = datetime.utcnow().isoformat() + "Z"
        self.updated_at: str = self.created_at
        self.updated_by: str = "Rulebricks Forge SDK"
        self.slug: str = self._generate_slug()
        self.folder_id: Optional[str] = None
        self.settings = {}
        self.form = {}
        self.history = []
        self.published = False
        self.published_at = None
        self.test_suite = []
        self.access_groups = []

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
        rule.settings = data.get('settings', {})
        rule.form = data.get('form', {})
        rule.history = data.get('history', [])
        rule.groups = data.get('groups', {})
        rule.published = data.get('published', False)
        rule.published_at = data.get('publishedAt', None)
        rule.test_suite = data.get('testSuite', [])
        rule.test_suite = [RuleTest.from_json(test) for test in rule.test_suite]
        rule.access_groups = data.get('accessGroups', [])
        rule.test_request = data.get('testRequest', {})

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

    def set_folder(self, folder_name: str, create_if_missing: Optional[bool] = False) -> 'Rule':
        """Move this rule into a folder by a folder name"""
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to set a folder by name, check the Rule constructor")
        folders = self.workspace.assets.list_folders()
        folder = next((f for f in folders if f.name == folder_name), None)
        if not folder and create_if_missing:
            raise ValueError(f"Folder '{folder_name}' not found in your Rulebricks workspace, and create_if_missing is False")
        if not folder:
            # Ensure folder name is unique
            if any(f.name == folder_name for f in folders):
                raise ValueError("Folder name conflicts with an existing folder in your workspace. Folder names must be unique.")
            folder = self.workspace.assets.upsert_folder(name=folder_name, description="Created by Rulebricks Forge SDK")
        self.folder_id = folder.id
        return self

    def set_folder_id(self, folder_id: str) -> 'Rule':
        """Move this rule into a folder by a folder ID"""
        self.folder_id = folder_id
        return self

    def set_alias(self, alias: str) -> 'Rule':
        """Override the generated API slug for this rule with a custom alias"""
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to set an alias, check the Rule constructor")
        if len(alias) < 3:
            raise ValueError("Alias must be at least 3 characters long")
        if not alias.isalnum():
            raise ValueError("Alias must be alphanumeric")
        if '/' in alias or '\\' in alias or ' ' in alias:
            raise ValueError("Alias cannot contain slashes or spaces")
        rules = self.workspace.assets.list_rules()
        if any(r.slug == alias for r in rules):
            raise ValueError("Alias conflicts with an existing rule in your workspace. Aliases must be unique.")

        if not all(c in string.ascii_letters + string.digits for c in alias):
            raise ValueError("Alias cannot contain special characters of any kind")

        self.slug = alias
        return self

    def add_access_group(self, group_name: str, create_if_missing: Optional[bool] = False) -> 'Rule':
        """Adds a user group to this rule that can be used to control who can access it"""
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to add access groups, check the Rule constructor")
        existing_access_groups = self.workspace.users.list_groups()
        group = next((g for g in existing_access_groups if g.name == group_name), None)
        if group:
            self.access_groups.append(group.name)
        if not group and not create_if_missing:
            raise ValueError(f"User group '{group_name}' not found in your Rulebricks workspace, and create_if_missing is False")
        if not group and create_if_missing:
            created_group = self.workspace.users.create_group(name=group_name, description="Created by Rulebricks Forge SDK")
            self.access_groups.append(created_group.name)

        return self

    def remove_access_group(self, group_name: str) -> 'Rule':
        """Removes a user group from this rule"""
        if group_name in self.access_groups:
            self.access_groups.remove(group_name)
        return self

    def enable_continous_testing(self, enabled: bool = True) -> 'Rule':
        """Require all critical tests to pass before publishing new versions of this rule"""
        self.settings["testing"] = enabled
        return self

    def enable_schema_validation(self, enabled: bool = True) -> 'Rule':
        """Enforce type validation on request data submitted to this rule before solving rules"""
        self.settings["schemaValidation"] = enabled
        return self

    def require_all_properties(self, enabled: bool = True) -> 'Rule':
        """Require all properties defined in the request schema to be present in the request before solving rules"""
        self.settings["allProperties"] = enabled
        return self

    def lock_schema(self, enabled: bool = True) -> 'Rule':
        """Disable altering the request and response schemas in the visual editor to prevent unintentional changes"""
        self.settings["lockSchema"] = enabled
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

    def when(self, **conditions) -> Condition:
        """Start defining a new condition"""
        return Condition(self, conditions=conditions)

    def any(self, **conditions) -> Condition:
        """Start defining a new condition with an OR operator"""
        return Condition(self, conditions=conditions, settings={"or": True})

    def get_condition(self, index: int) -> Condition:
        """Get a condition by index for modification"""
        if index < 0 or index >= len(self.conditions):
            raise ValueError(f"Condition index {index} out of range")
        return Condition(
            rule=self,
            conditions=self.conditions[index].get("request", {}),
            index=index,
            settings=self.conditions[index].get("settings", {})
        )

    def find_conditions(self, **kwargs) -> List[Condition]:
        """Find conditions matching certain criteria"""
        results = []
        for i, condition in enumerate(self.conditions):
            matches = True
            for field, value in kwargs.items():
                if field not in condition["request"]:
                    matches = False
                    break
                if condition["request"][field]["op"] != value:
                    matches = False
                    break
            if matches:
                results.append(Condition(
                    rule=self,
                    conditions=condition.get("request", {}),
                    index=i,
                    settings=condition.get("settings", {})
                ))
        return results

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
            "tag": self.folder_id,
            "slug": self.slug,
            "createdAt": self.created_at,
            "updatedAt": self.updated_at,
            "updatedBy": self.updated_by,
            "published": self.published,
            "publishedAt": self.published_at,
            "sampleRequest": sampleRequest,
            "sampleResponse": sampleResponse,
            "testRequest": self.test_request or sampleRequest,
            "requestSchema": [
                {
                    "key": name,
                    "name": field.name.replace('_', ' ').title(),
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
                    "name": field.name.replace('_', ' ').title(),
                    "type": self._get_field_type(field).value,
                    "description": field.description,
                    "defaultValue": field.default,
                    "show": True
                }
                for name, field in self.response_fields.items()
            ],
            "conditions": self.conditions,
            "form": self.form,
            "history": self.history,
            "settings": self.settings,
            "testSuite": [test.to_dict() for test in self.test_suite],
            "groups": self.groups,
            "no_conditions": len(self.conditions),
            "accessGroups": self.access_groups
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

    def get_editor_url(self, base_url = "https://rulebricks.com") -> str:
        """Get the editor URL to edit this in the Rulebricks web app (if imported)"""
        return f"{base_url}/dashboard/{self.id}"
