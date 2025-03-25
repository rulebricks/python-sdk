from .types.operators import RuleType
from .operators import BooleanField, NumberField, StringField, DateField, ListField, Argument
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
    from ..client import Rulebricks

def process_dynamic_values(arg: Any) -> Any:
    """
    Process any argument into the correct format for conditions.

    This function recursively processes arguments to handle DynamicValue instances,
    Argument instances, lists, and dictionaries, converting them into the appropriate
    format for use in rule conditions.

    Args:
        arg (Any): The argument to process. Can be a DynamicValue, Argument, list,
                  dictionary, or any other type.

    Returns:
        Any: The processed argument in the correct format for conditions.
              - For DynamicValue instances: Returns the dictionary representation
              - For Argument instances: Returns the processed value
              - For lists: Returns a list with all items processed
              - For dictionaries: Returns a dict with all values processed
              - For other types: Returns the original value unchanged
    """
    if isinstance(arg, DynamicValue):
        return arg.to_dict()
    elif isinstance(arg, Argument):
        return arg.value if not isinstance(arg.value, DynamicValue) else arg.value.to_dict()
    elif isinstance(arg, list):
        return [process_dynamic_values(item) for item in arg]
    elif isinstance(arg, dict):
        return {k: process_dynamic_values(v) for k, v in arg.items()}
    return arg

class Condition:
    """
    A class for building and modifying rule conditions.

    The Condition class represents a single condition within a rule, containing both
    the conditions that trigger it and the responses that should occur when those
    conditions are met.

    Attributes:
        rule (Rule): The parent rule this condition belongs to.
        conditions (Dict): Dictionary of field conditions.
        index (Optional[int]): Index of this condition in the parent rule's condition list.
        responses (Dict): Dictionary of response values.
        settings (Dict): Condition settings including enabled state, group ID, priority, and schedule.
    """

    def __init__(
            self,
            rule: 'Rule',
            conditions: Optional[Dict] = None,
            index: Optional[int] = None,
            settings: Optional[Dict] = None
        ):
        """
        Initialize a new Condition instance.

        Args:
            rule (Rule): The parent rule this condition belongs to.
            conditions (Optional[Dict]): Initial conditions dictionary. Defaults to empty dict.
            index (Optional[int]): Index of this condition in the parent rule's condition list.
                                 None for new conditions.
            settings (Optional[Dict]): Initial settings dictionary. Defaults to None.
        """
        self.rule = rule
        self.conditions = conditions if conditions is not None else {}
        self.index = index  # None for new conditions, index for editing existing
        self.responses = {}
        self.settings = {"enabled": True, "groupId": None, "priority": 0, "schedule": []}
        if settings is not None:
            self.settings.update(settings)

    def when(self, **conditions) -> 'Condition':
        """
        Set or update conditions for this rule condition.

        Args:
            **conditions: Keyword arguments where each key is a field name and each value
                        is a tuple of (operator, arguments) defining the condition.

        Returns:
            Condition: The current condition instance for method chaining.

        Raises:
            ValueError: If a field name is not defined in the request schema.

        Example:
            >>> condition.when(age=('greater_than', [18]))
        """
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
        """
        Set or update responses for this condition.

        Args:
            **responses: Keyword arguments where each key is a field name and each value
                       is the response value to set when the condition is met.

        Returns:
            Union[Rule, Condition]: The parent Rule instance for new conditions, or the
                                  current Condition instance for existing conditions.

        Raises:
            ValueError: If a field name is not defined in the response schema.

        Example:
            >>> condition.then(approved=True, message="Access granted")
        """
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
        """
        Set the priority level for this condition.

        Args:
            priority (int): The priority level to set. Higher numbers indicate higher priority.

        Returns:
            Condition: The current condition instance for method chaining.
        """
        self.settings["priority"] = priority
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["priority"] = priority
        return self

    def enable(self) -> 'Condition':
        """
        Enable this condition.

        Returns:
            Condition: The current condition instance for method chaining.
        """
        self.settings["enabled"] = True
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["enabled"] = True
        return self

    def disable(self) -> 'Condition':
        """
        Disable this condition.

        Returns:
            Condition: The current condition instance for method chaining.
        """
        self.settings["enabled"] = False
        if self.index is not None:
            self.rule.conditions[self.index]["settings"]["enabled"] = False
        return self

    def delete(self) -> None:
        """
        Remove this condition from its parent rule.

        Raises:
            IndexError: If the condition's index is invalid.
        """
        if self.index is not None:
            self.rule.conditions.pop(self.index)

    def __repr__(self) -> str:
        """
        Get a string representation of this condition.

        Returns:
            str: A string representation indicating whether this is a new or existing condition.
        """
        if self.index is not None:
            return f"<Condition: Row {self.index}>"
        return "<Condition: New>"

    def to_table(self) -> str:
        """
        Generate a tabular representation of this condition.

        Returns:
            str: A formatted string containing the condition's fields and values in a grid layout.
        """
        from tabulate import tabulate

        # Get all field names for headers
        headers = list(self.rule.request_fields.keys()) + list(self.rule.response_fields.keys())
        table_data = []

        condition = None
        if self.index is not None:
            condition = self.rule.conditions[self.index]
        else:
            condition = {
                "request": self.conditions,
                "response": self.responses
            }

        row = []

        # Add request field values
        for field_name in self.rule.request_fields.keys():
            if field_name in condition["request"]:
                rule = condition["request"][field_name]
                op_name = rule["op"]
                args_str = ", ".join(map(str, rule["args"]))
                row.append(f"{op_name}\n({args_str})")
            else:
                row.append("-")

        # Add response field values
        for field_name in self.rule.response_fields.keys():
            if field_name in condition["response"]:
                row.append(condition["response"][field_name]["value"])
            else:
                row.append("-")

        table_data.append(row)

        return tabulate(table_data, headers=headers, tablefmt="grid")

class RuleTest:
    """
    A class for defining and managing test cases for rules.

    RuleTest allows users to define test cases that verify a rule's behavior by
    specifying input requests and expected responses.

    Attributes:
        id (str): Unique identifier for the test.
        name (str): Human-readable name for the test.
        request (Dict): Test input request payload.
        response (Dict): Expected response payload.
        critical (bool): Whether this test is critical for rule validation.
        last_executed (Optional[datetime]): When the test was last run.
        test_state (Optional[str]): Current state of the test.
        error (Optional[str]): Error message if test failed.
        success (Optional[bool]): Whether the test passed or failed.
    """

    def __init__(self):
        """Initialize a new RuleTest instance with default values."""
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
        """
        Generate a random unique identifier for the test.

        Returns:
            str: A 21-character random string of letters and numbers.
        """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=21))

    def set_name(self, name: str) -> 'RuleTest':
        """
        Set the name of the test.

        Args:
            name (str): The new name for the test.

        Returns:
            RuleTest: The current test instance for method chaining.
        """
        self.name = name
        return self

    def expect(self, request: Dict[str, Any], response: Dict[str, Any]) -> 'RuleTest':
        """
        Set the test request and expected response payloads.

        Args:
            request (Dict[str, Any]): The input request payload for the test.
            response (Dict[str, Any]): The expected response payload.

        Returns:
            RuleTest: The current test instance for method chaining.
        """
        self.request = request
        self.response = response
        return self

    def is_critical(self, critical: bool = True) -> 'RuleTest':
        """
        Set whether this test is critical for rule validation.

        Args:
            critical (bool): Whether the test is critical. Defaults to True.

        Returns:
            RuleTest: The current test instance for method chaining.
        """
        self.critical = critical
        return self

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the test to a dictionary representation.

        Returns:
            Dict[str, Any]: Dictionary containing all test attributes.
        """
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
        Create a RuleTest instance from JSON data.

        Args:
            json_str (Union[str, Dict[str, Any]]): Either a JSON string or dictionary
                                                  containing test data.

        Returns:
            RuleTest: A new RuleTest instance populated with the data.

        Raises:
            ValueError: If the JSON data is invalid or missing required fields.
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
    """
    Main class for building and managing business rules.

    The Rule class provides a comprehensive interface for defining, modifying, and
    managing business rules including their conditions, fields, tests, and metadata.

    Attributes:
        workspace (Optional[Rulebricks]): Connected Rulebricks workspace client.
        request_fields (Dict): Dictionary of input fields for the rule.
        response_fields (Dict): Dictionary of output fields for the rule.
        test_request (Optional[Dict]): Sample request for testing.
        conditions (List[Dict]): List of rule conditions.
        groups (Dict): Rule groups configuration.
        name (str): Name of the rule.
        description (str): Description of the rule.
        id (str): Unique identifier for the rule.
        created_at (str): ISO timestamp of creation.
        updated_at (str): ISO timestamp of last update.
        updated_by (str): Identity of last updater.
        slug (str): URL-friendly identifier.
        folder_id (Optional[str]): ID of containing folder.
        settings (Dict): Rule settings.
        form (Dict): Form configuration.
        history (List): Change history.
        published (bool): Whether the rule is published.
        published_at (Optional[str]): ISO timestamp of last publish.
        test_suite (List[RuleTest]): List of test cases.
        access_groups (List[str]): List of groups with access.
        published_conditions (List): Published version of conditions.
        published_request_schema (List): Published version of request schema.
        published_response_schema (List): Published version of response schema.
        published_groups (Dict): Published version of groups.
    """

    def __init__(self, rulebricks_client: Optional['Rulebricks'] = None):
        """
        Initialize a new Rule instance.

        Args:
            rulebricks_client (Optional[Rulebricks]): A connected Rulebricks workspace client.
                                                        Defaults to None.
        """
        self.workspace = rulebricks_client
        self.request_fields = {}
        self.response_fields = {}
        self.test_request = None
        self.conditions = []
        self.groups = {}
        self.name = "Untitled Rule"
        self.description = ""
        self.id = str(uuid.uuid4())
        self.created_at = datetime.utcnow().isoformat() + "Z"
        self.updated_at = self.created_at
        self.updated_by = "Rulebricks Forge SDK"
        self.slug = self._generate_slug()
        self.folder_id = None
        self.settings = {}
        self.form = {}
        self.history = []
        self.published = False
        self.published_at = None
        self.test_suite = []
        self.access_groups = []
        self.published_conditions = []
        self.published_request_schema = []
        self.published_response_schema = []
        self.published_groups = {}

    def set_workspace(self, rulebricks_client: Any) -> None:
        """
        Supply the rule with a connection to a Rulebricks workspace.

        Args:
            rulebricks_client (Any): The Rulebricks workspace client to connect.

        Returns:
            None
        """
        self.workspace = rulebricks_client
        return

    def __repr__(self) -> str:
        """
        Get a string representation of this rule.

        Returns:
            str: A string showing the rule's name.
        """
        return f"<Rule: {self.name}>"

    @classmethod
    def from_json(cls, json_str: Union[str, Dict[str, Any]]) -> 'Rule':
        """
        Create a Rule instance from JSON data.

        Args:
            json_str (Union[str, Dict[str, Any]]): Either a JSON string or dictionary
                                                  containing rule data.

        Returns:
            Rule: A new Rule instance populated with the data.

        Raises:
            ValueError: If the JSON data is invalid or missing required fields.

        Example:
            >>> rule = Rule.from_json('{"name": "My Rule", "conditions": []}')
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
        rule.folder_id = data.get('tag', None)
        rule.published_conditions = data.get('publishedConditions', [])
        rule.published_request_schema = data.get('publishedRequestSchema', [])
        rule.published_response_schema = data.get('publishedResponseSchema', [])
        rule.published_groups = data.get('publishedGroups', {})

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

    def from_workspace(self, rule_id: str) -> 'Rule':
        """
        Load a rule from the connected workspace by ID.

        Args:
            rule_id (str): The unique identifier of the rule to load.

        Returns:
            Rule: The loaded rule instance.

        Raises:
            ValueError: If the workspace client is missing or the rule cannot be found.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to load a rule from the workspace")
        rule_data = self.workspace.assets.rules.pull(id=rule_id)
        return Rule.from_json(rule_data)

    def update(self) -> 'Rule':
        """
        Push local changes to this rule to the connected workspace.

        Returns:
            Rule: The current rule instance for method chaining.

        Raises:
            ValueError: If the workspace client is missing or the rule cannot be pushed.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to push a rule to the workspace. See Rule.set_workspace()")
        self.workspace.assets.rules.push(rule=self.to_dict())
        self = self.from_workspace(rule_id=self.id)
        return self

    def publish(self) -> 'Rule':
        """
        Publish a new version of this rule in the connected workspace.

        Returns:
            Rule: The current rule instance for method chaining.

        Raises:
            ValueError: If the workspace client is missing or the rule cannot be published.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to publish a rule. See Rule.set_workspace()")
        rule_dict = self.to_dict()
        # Flag the rule to publish a *new* version
        # Note this is different from self.published
        rule_dict["_publish"] = True
        self.workspace.assets.rules.push(rule=rule_dict)
        self = self.from_workspace(rule_id=self.id)
        return self

    def _generate_slug(self, length: int = 10) -> str:
        """
        Generate a random alphanumeric slug for the rule.

        Args:
            length (int): Length of the slug to generate. Defaults to 10.

        Returns:
            str: A random string of alphanumeric characters.
        """
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(length))

    def _get_field_type(self, field: Union[BooleanField, NumberField, StringField, DateField, ListField]) -> RuleType:
        """
        Get the RuleType enum value for a field.

        Args:
            field (Union[BooleanField, NumberField, StringField, DateField, ListField]):
                The field to get the type for.

        Returns:
            RuleType: The corresponding RuleType enum value.
        """
        type_mapping = {
            BooleanField: RuleType.BOOLEAN,
            NumberField: RuleType.NUMBER,
            StringField: RuleType.STRING,
            DateField: RuleType.DATE,
            ListField: RuleType.LIST
        }
        return type_mapping[field.__class__]

    def set_name(self, name: str) -> 'Rule':
        """
        Set the rule name.

        Args:
            name (str): The new name for the rule.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.name = name
        return self

    def set_description(self, description: str) -> 'Rule':
        """
        Set the rule description.

        Args:
            description (str): The new description for the rule.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.description = description
        return self

    def set_folder(self, folder_name: str, create_if_missing: Optional[bool] = False) -> 'Rule':
        """
        Move this rule into a folder by folder name.

        Args:
            folder_name (str): Name of the target folder.
            create_if_missing (Optional[bool]): Whether to create the folder if it doesn't exist.
                                              Defaults to False.

        Returns:
            Rule: The current rule instance for method chaining.

        Raises:
            ValueError: If workspace client is missing or folder conflicts exist.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to set a folder by name")
        folders = self.workspace.assets.folders.list()
        folder = next((f for f in folders if f.name == folder_name), None)
        if not folder and create_if_missing:
            if any(f.name == folder_name for f in folders):
                raise ValueError("Folder name conflicts with an existing folder")
            folder = self.workspace.assets.folders.upsert(name=folder_name)
        if not folder:
            raise ValueError(f"Folder '{folder_name}' not found and create_if_missing is False")
        self.folder_id = folder.id
        return self

    def set_folder_id(self, folder_id: str) -> 'Rule':
        """
        Move this rule into a folder by folder ID.

        Args:
            folder_id (str): ID of the target folder.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.folder_id = folder_id
        return self

    def set_alias(self, alias: str) -> 'Rule':
        """
        Override the generated API slug with a custom alias.

        Args:
            alias (str): The custom alias to use.

        Returns:
            Rule: The current rule instance for method chaining.

        Raises:
            ValueError: If the alias is invalid or conflicts with existing rules.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to set an alias")
        if len(alias) < 3:
            raise ValueError("Alias must be at least 3 characters long")
        if '/' in alias or '\\' in alias or ' ' in alias:
            raise ValueError("Alias cannot contain slashes or spaces")
        if not all(c in string.ascii_letters + string.digits + '-' for c in alias):
            raise ValueError("Alias cannot contain special characters")

        rules = self.workspace.assets.rules.list()
        if any(r.slug == alias for r in rules):
            raise ValueError("Alias conflicts with an existing rule")

        self.slug = alias
        return self

    def add_access_group(self, group_name: str, create_if_missing: Optional[bool] = False) -> 'Rule':
        """
        Add a user group that can access this rule.

        Args:
            group_name (str): Name of the group to add.
            create_if_missing (Optional[bool]): Whether to create the group if it doesn't exist.
                                              Defaults to False.

        Returns:
            Rule: The current rule instance for method chaining.

        Raises:
            ValueError: If workspace client is missing or group operations fail.
        """
        if not self.workspace:
            raise ValueError("A Rulebricks client is required to add access groups")
        existing_access_groups = self.workspace.users.groups.list()
        group = next((g for g in existing_access_groups if g.name == group_name), None)
        if group:
            self.access_groups.append(group.name)
        if not group and not create_if_missing:
            raise ValueError(f"User group '{group_name}' not found and create_if_missing is False")
        if not group and create_if_missing:
            created_group = self.workspace.users.groups.create(name=group_name)
            self.access_groups.append(created_group.name)
        return self

    def remove_access_group(self, group_name: str) -> 'Rule':
        """
        Remove a user group's access to this rule.

        Args:
            group_name (str): Name of the group to remove.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        if group_name in self.access_groups:
            self.access_groups.remove(group_name)
        return self

    def enable_continous_testing(self, enabled: bool = True) -> 'Rule':
        """
        Configure whether critical tests must pass before publishing.

        Args:
            enabled (bool): Whether to enable continuous testing. Defaults to True.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.settings["testing"] = enabled
        return self

    def enable_schema_validation(self, enabled: bool = True) -> 'Rule':
        """
        Configure whether to validate request data against the schema.

        Args:
            enabled (bool): Whether to enable schema validation. Defaults to True.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.settings["schemaValidation"] = enabled
        return self

    def require_all_properties(self, enabled: bool = True) -> 'Rule':
        """
        Configure whether all schema properties must be present in requests.

        Args:
            enabled (bool): Whether to require all properties. Defaults to True.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.settings["allProperties"] = enabled
        return self

    def lock_schema(self, enabled: bool = True) -> 'Rule':
        """
        Configure whether the schema can be modified in the visual editor.

        Args:
            enabled (bool): Whether to lock the schema. Defaults to True.

        Returns:
            Rule: The current rule instance for method chaining.
        """
        self.settings["lockSchema"] = enabled
        return self

    def add_boolean_field(self, name: str, description: str = "", default: bool = False) -> BooleanField:
        """
        Add a boolean request field to the rule.

        Args:
            name (str): Name/key of the field.
            description (str): Description of the field. Defaults to empty string.
            default (bool): Default value for the field. Defaults to False.

        Returns:
            BooleanField: The created field instance.

        Example:
            >>> rule.add_boolean_field('is_active', 'Whether the account is active', True)
        """
        field = BooleanField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_number_field(self, name: str, description: str = "", default: Union[int, float] = 0) -> NumberField:
        """
        Add a number request field to the rule.

        Args:
            name (str): Name/key of the field.
            description (str): Description of the field. Defaults to empty string.
            default (Union[int, float]): Default value for the field. Defaults to 0.

        Returns:
            NumberField: The created field instance.

        Example:
            >>> rule.add_number_field('age', 'Age in years', 18)
        """
        field = NumberField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_string_field(self, name: str, description: str = "", default: str = "") -> StringField:
        """
        Add a string field to the rule's request schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in request payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (str): Default value for the field if none is provided in the request.
                            Defaults to empty string.

        Returns:
            StringField: The created string field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_string_field("username", "User's login name", "guest")
        """
        field = StringField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_date_field(self, name: str, description: str = "", default: Optional[datetime] = None) -> DateField:
        """
        Add a date field to the rule's request schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in request payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (Optional[datetime]): Default value for the field if none is provided
                                        in the request. Defaults to None.

        Returns:
            DateField: The created date field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> from datetime import datetime
            >>> rule.add_date_field("created_at", "Record creation date", datetime.now())
        """
        field = DateField(name, description, default)
        self.request_fields[name] = field
        return field

    def add_list_field(self, name: str, description: str = "", default: Optional[List] = None) -> ListField:
        """
        Add a list field to the rule's request schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in request payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (Optional[List]): Default value for the field if none is provided
                                    in the request. Defaults to None, which will be
                                    converted to an empty list.

        Returns:
            ListField: The created list field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_list_field("tags", "Item categories", ["default", "basic"])
        """
        field = ListField(name, description, default or [])
        self.request_fields[name] = field
        return field

    def add_boolean_response(self, name: str, description: str = "", default: bool = False) -> BooleanField:
        """
        Add a boolean field to the rule's response schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in response payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (bool): Default value for the field if none is set by conditions.
                            Defaults to False.

        Returns:
            BooleanField: The created boolean field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_boolean_response("is_approved", "Whether the request was approved", False)
        """
        field = BooleanField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_number_response(self, name: str, description: str = "", default: Union[int, float] = 0) -> NumberField:
        """
        Add a number field to the rule's response schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in response payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (Union[int, float]): Default value for the field if none is set by conditions.
                                        Defaults to 0.

        Returns:
            NumberField: The created number field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_number_response("total_amount", "Calculated total", 0.0)
        """
        field = NumberField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_string_response(self, name: str, description: str = "", default: str = "") -> StringField:
        """
        Add a string field to the rule's response schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in response payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (str): Default value for the field if none is set by conditions.
                            Defaults to empty string.

        Returns:
            StringField: The created string field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_string_response("message", "Response message to user", "Success")
        """
        field = StringField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_date_response(self, name: str, description: str = "", default: Optional[datetime] = None) -> DateField:
        """
        Add a date field to the rule's response schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in response payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (Optional[datetime]): Default value for the field if none is set by conditions.
                                        Defaults to None.

        Returns:
            DateField: The created date field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_date_response("processed_at", "Time of processing")
        """
        field = DateField(name, description, default)
        self.response_fields[name] = field
        return field

    def add_list_response(self, name: str, description: str = "", default: Optional[List] = None) -> ListField:
        """
        Add a list field to the rule's response schema.

        Args:
            name (str): The name/identifier for the field. This will be used as the key
                        in response payloads.
            description (str): Optional description of the field's purpose or usage.
                                Defaults to empty string.
            default (Optional[List]): Default value for the field if none is set by conditions.
                                    Defaults to None, which will be converted to an empty list.

        Returns:
            ListField: The created list field instance.

        Raises:
            ValueError: If a field with the same name already exists.

        Example:
            >>> rule.add_list_response("errors", "List of validation errors", [])
        """
        field = ListField(name, description, default or [])
        self.response_fields[name] = field
        return field

    def when(self, **conditions) -> Condition:
        """
        Start defining a new condition for the rule.

        Args:
            **conditions: Keyword arguments defining initial conditions. Each key should be
                        a field name and each value should be a tuple of (operator, arguments).

        Returns:
            Condition: A new condition instance for building the complete condition.

        Example:
            >>> rule.when(age=('greater_than', [21]), status=('equals', ['active']))
        """
        return Condition(self, conditions=conditions)

    def any(self, **conditions) -> Condition:
        """
        Start defining a new condition with an OR operator.

        Similar to when(), but creates a condition that will be evaluated with OR logic
        instead of the default AND logic.

        Args:
            **conditions: Keyword arguments defining initial conditions. Each key should be
                        a field name and each value should be a tuple of (operator, arguments).

        Returns:
            Condition: A new condition instance configured for OR logic.

        Example:
            >>> rule.any(status=('equals', ['pending']), priority=('equals', ['high']))
        """
        return Condition(self, conditions=conditions, settings={"or": True})

    def get_condition(self, index: int) -> Condition:
        """
        Get an existing condition by its index for modification.

        Args:
            index (int): The zero-based index of the condition to retrieve.

        Returns:
            Condition: The condition instance at the specified index.

        Raises:
            ValueError: If the index is out of range.

        Example:
            >>> condition = rule.get_condition(0)
            >>> condition.disable()
        """
        if index < 0 or index >= len(self.conditions):
            raise ValueError(f"Condition index {index} out of range")
        return Condition(
            rule=self,
            conditions=self.conditions[index].get("request", {}),
            index=index,
            settings=self.conditions[index].get("settings", {})
        )

    def get_boolean_field(self, name: str) -> BooleanField:
        """
        Get a boolean field from the rule's request schema by name.

        Args:
            name (str): The name of the field to retrieve.

        Returns:
            BooleanField: The requested boolean field.

        Raises:
            ValueError: If the field doesn't exist or isn't a boolean field.

        Example:
            >>> is_active = rule.get_boolean_field("is_active")
            >>> matched_conditions = rule.find_conditions(is_active=is_active.equals(True))
        """
        if name not in self.request_fields:
            raise ValueError(f"Field '{name}' not found in request schema")
        elif not isinstance(self.request_fields[name], BooleanField):
            raise ValueError(f"Field '{name}' is not a boolean field")
        return self.request_fields[name] # type: ignore

    def get_number_field(self, name: str) -> NumberField:
        """
        Get a number field from the rule's request schema by name.

        Args:
            name (str): The name of the field to retrieve.

        Returns:
            NumberField: The requested number field.

        Raises:
            ValueError: If the field doesn't exist or isn't a number field.

        Example:
            >>> amount = rule.get_number_field("amount")
            >>> matched_conditions = rule.find_conditions(amount=amount.greater_than(1000))
        """
        if name not in self.request_fields:
            raise ValueError(f"Field '{name}' not found in request schema")
        elif not isinstance(self.request_fields[name], NumberField):
            raise ValueError(f"Field '{name}' is not a number field")
        return self.request_fields[name] # type: ignore

    def get_string_field(self, name: str) -> StringField:
        """
        Get a string field from the rule's request schema by name.

        Args:
            name (str): The name of the field to retrieve.

        Returns:
            StringField: The requested string field.

        Raises:
            ValueError: If the field doesn't exist or isn't a string field.

        Example:
            >>> status = rule.get_string_field("status")
            >>> matched_condtions = rule.find_conditions(status=status.equals("active"))
        """
        if name not in self.request_fields:
            raise ValueError(f"Field '{name}' not found in request schema")
        elif not isinstance(self.request_fields[name], StringField):
            raise ValueError(f"Field '{name}' is not a string field")
        return self.request_fields[name] # type: ignore

    def get_date_field(self, name: str) -> DateField:
        """
        Get a date field from the rule's request schema by name.

        Args:
            name (str): The name of the field to retrieve.

        Returns:
            DateField: The requested date field.

        Raises:
            ValueError: If the field doesn't exist or isn't a date field.

        Example:
            >>> created_at = rule.get_date_field("created_at")
            >>> matched_conditions = rule.find_conditions(created_at=created_at.before(
            ...     datetime(2021, 1, 1)
            ... ))
        """
        if name not in self.request_fields:
            raise ValueError(f"Field '{name}' not found in request schema")
        elif not isinstance(self.request_fields[name], DateField):
            raise ValueError(f"Field '{name}' is not a date field")
        return self.request_fields[name] # type: ignore

    def get_list_field(self, name: str) -> ListField:
        """
        Get a list field from the rule's request schema by name.

        Args:
            name (str): The name of the field to retrieve.

        Returns:
            ListField: The requested list field.

        Raises:
            ValueError: If the field doesn't exist or isn't a list field.

        Example:
            >>> tags = rule.get_list_field("tags")
            >>> matched_conditions = rule.find_conditions(tags=tags.contains("important"))
        """
        if name not in self.request_fields:
            raise ValueError(f"Field '{name}' not found in request schema")
        elif not isinstance(self.request_fields[name], ListField):
            raise ValueError(f"Field '{name}' is not a list field")
        return self.request_fields[name] # type: ignore

    def find_conditions(self, **kwargs) -> List[Condition]:
        """
        Find conditions matching specified criteria using field operators.

        This method searches through existing conditions and returns those that match
        all the specified criteria.

        Args:
            **kwargs: Keyword arguments where each key is a field name and each value
                        is a tuple of (operator, arguments) to match against.

        Returns:
            List[Condition]: List of matching condition instances.

        Example:
            >>> # Find all conditions where age > 18 and status = "active"
            >>> matched_conditions = created_rule.find_conditions(
            ...     age=created_rule.get_number_field("age").greater_than(18),
            ...     status=created_rule.get_string_field("status").equals("active")
            ... )
            >>> matched_conditions[0].then(
            ...     estimated_premium=3000
            ... )
        """
        results = []
        for i, condition in enumerate(self.conditions):
            matches = True
            for field, (operator, args) in kwargs.items():
                if field not in condition["request"]:
                    matches = False
                    break
                request = condition["request"][field]
                if request["op"] != operator:
                    matches = False
                    break
                # Compare args (ignoring DynamicValues)
                if any(isinstance(a, DynamicValue) for a in args):
                    continue
                # Convert both sets of args to strings for comparison
                existing_args = [str(arg) for arg in request["args"]]
                search_args = [str(arg) for arg in args]
                if existing_args != search_args:
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
        """
        Convert the rule to a dictionary representation.

        This method generates a complete dictionary representation of the rule,
        including all fields, conditions, settings, and metadata. This format
        is suitable for serialization and API communication.

        Returns:
            Dict[str, Any]: Complete dictionary representation of the rule.

        Example:
            >>> rule_dict = rule.to_dict()
            >>> print(rule_dict['name'], rule_dict['conditions'])
        """
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
            "published_requestSchema": self.published_request_schema,
            "published_responseSchema": self.published_response_schema,
            "published_conditions": self.published_conditions,
            "published_groups": self.published_groups,
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
        """
        Convert the rule to a JSON string representation.

        This method serializes the complete rule into a formatted JSON string,
        suitable for file storage or API transmission.

        Returns:
            str: JSON string representation of the rule.

        Example:
            >>> json_str = rule.to_json()
            >>> with open('rule.json', 'w') as f:
            ...     f.write(json_str)
        """
        return json.dumps(self.to_dict(), indent=2, default=str)

    def to_table(self) -> str:
        """
        Generate a tabular representation of all rule conditions.

        Creates a formatted grid view showing all conditions and their
        corresponding responses, suitable for console output or logging.

        Returns:
            str: A string containing the tabular representation of the rule.

        Example:
            >>> print(rule.to_table())
            +----------------+----------------+----------------+
            | age           | status         | approved       |
            +================+================+================+
            | greater_than  | equals         | True          |
            | (18)          | ("active")     |               |
            +----------------+----------------+----------------+
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
                    arguments_repr = []
                    for arg in rule["args"]:
                        if isinstance(arg, Dict) and "$rb" in arg:
                            arguments_repr.append(arg["name"].upper())
                        else:
                            arguments_repr.append(str(arg))
                    args_str = ", ".join(arguments_repr)
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
        Export the rule to a file in the specified directory.

        Creates a JSON file containing the complete rule definition. The filename
        is automatically generated based on the rule name with a unique suffix if
        needed to avoid conflicts.

        Args:
            directory (Optional[str]): Directory where the file should be saved.
                                        If None, uses the current directory.

        Returns:
            str: The path to the exported file.

        Example:
            >>> file_name = rule.export()
            >>> print(f"Rule exported to {file_name}")
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
        """
        Get the URL for editing this rule in the Rulebricks web app.

        Args:
            base_url (str): Base URL for the Rulebricks application.
                            Defaults to "https://rulebricks.com".

        Returns:
            str: Complete URL for editing the rule.

        Example:
            >>> url = rule.get_editor_url()
            >>> print(f"Edit rule at: {url}")
        """
        return f"{base_url}/dashboard/{self.id}"

    def find_test_by_name(self, name: str) -> Optional[RuleTest]:
        """
        Find a test case by its name.

        Args:
            name (str): The name of the test to find.

        Returns:
            Optional[RuleTest]: The matching test case, or None if not found.

        Example:
            >>> test = rule.find_test_by_name("Check age validation")
            >>> if test:
            ...     print(f"Test found: {test.name}")
        """
        return next((t for t in self.test_suite if t.name == name), None)

    def find_test_by_id(self, test_id: str) -> Optional[RuleTest]:
        """
        Find a test case by its ID.

        Args:
            test_id (str): The ID of the test to find.

        Returns:
            Optional[RuleTest]: The matching test case, or None if not found.

        Example:
            >>> test = rule.find_test_by_id("abc123")
            >>> if test:
            ...     print(f"Test found: {test.name}")
        """
        return next((t for t in self.test_suite if t.id == test_id), None)

    def add_test(self, test: RuleTest) -> 'Rule':
        """
        Add a test case to the rule's test suite or update an existing one.

        If a test with the same ID already exists, it will be updated with
        the new test's values. Otherwise, the new test will be added to
        the suite.

        Args:
            test (RuleTest): The test case to add or update.

        Returns:
            Rule: The rule instance for method chaining.

        Example:
            >>> new_test = RuleTest().set_name("Adult check")
            >>> rule.add_test(new_test)
        """
        existing_test = self.find_test_by_id(test.id)
        if existing_test:
            existing_test.name = test.name
            existing_test.request = test.request
            existing_test.response = test.response
            existing_test.critical = test.critical
        else:
            self.test_suite.append(test)
        return self

    def remove_test(self, test_id: str) -> None:
        """
        Remove a test case from the rule's test suite.

        Args:
            test_id (str): The ID of the test to remove.

        Example:
            >>> rule.remove_test("abc123")
        """
        test = self.find_test_by_id(test_id)
        if test:
            self.test_suite.remove(test)
