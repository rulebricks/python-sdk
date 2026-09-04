from datetime import datetime
from types import SimpleNamespace
from unittest.mock import MagicMock, call

import pytest

from rulebricks.forge import (
    BooleanField,
    DateField,
    ListField,
    NumberField,
    Rule,
    StringField,
    TypeMismatchError,
    Vocabulary,
    VocabularyValue,
    VocabularyValueNotFoundError,
)
from rulebricks.forge.operators import Argument
from rulebricks.forge.rule import process_vocabulary_values
from rulebricks.forge.types import VocabularyValueType


PUBLISHED_KEYS = {
    "published_requestSchema",
    "published_responseSchema",
    "published_conditions",
    "published_groups",
}

EXPECTED_OPERATOR_WIRE_NAMES = {
    BooleanField: {
        "any",
        "is true",
        "is false",
        "is null",
    },
    NumberField: {
        "any",
        "equals",
        "does not equal",
        "greater than",
        "less than",
        "greater than or equal to",
        "less than or equal to",
        "between",
        "not between",
        "is included in",
        "is even",
        "is odd",
        "is positive",
        "is negative",
        "is zero",
        "is not zero",
        "is a multiple of",
        "is not a multiple of",
        "is a power of",
        "is null",
    },
    StringField: {
        "any",
        "contains",
        "does not contain",
        "equals",
        "equals (case-insensitive)",
        "does not equal",
        "does not equal (case-insensitive)",
        "is empty",
        "is not empty",
        "starts with",
        "ends with",
        "is included in",
        "is not included in",
        "contains any of",
        "does not contain any of",
        "is of length",
        "is not of length",
        "is longer than",
        "is shorter than",
        "is longer than or equal to",
        "is shorter than or equal to",
        "starts with (case-insensitive)",
        "ends with (case-insensitive)",
        "contains (case-insensitive)",
        "is a valid phone number",
        "is a valid zip code",
        "matches RegEx",
        "does not match RegEx",
        "is a work email address",
        "is a personal email address",
        "is a valid email address",
        "is not a valid email address",
        "is a valid URL",
        "is not a valid URL",
        "is a valid IP address",
        "is not a valid IP address",
        "is a valid IPV6 address",
        "is not a valid IPV6 address",
        "is a valid credit card number",
        "is not a valid credit card number",
        "is a valid country code",
        "is not a valid country code",
        "contains profanity",
        "does not contain profanity",
        "is uppercase",
        "is lowercase",
        "is numeric",
        "contains only digits",
        "contains only letters",
        "contains only digits and letters",
        "version is greater than",
        "version is less than",
        "version is equal to",
        "version is greater than or equal to",
        "version is less than or equal to",
        "version is between",
        "is valid semantic version",
        "satisfies version range",
        "is null",
    },
    DateField: {
        "any",
        "is in the past",
        "is in the future",
        "days ago",
        "is less than N days ago",
        "is more than N days ago",
        "is between N and M days ago",
        "days from now",
        "is less than N days from now",
        "is more than N days from now",
        "months ago",
        "is less than N months ago",
        "is more than N months ago",
        "is between N and M months ago",
        "months from now",
        "is less than N months from now",
        "is more than N months from now",
        "is today",
        "is this week",
        "is this month",
        "is this year",
        "is next week",
        "is next month",
        "is next year",
        "is last week",
        "is last month",
        "is last year",
        "after",
        "on or after",
        "before",
        "on or before",
        "between",
        "not between",
        "equals",
        "does not equal",
        "is before time",
        "is after time",
        "hours ago",
        "is less than N hours ago",
        "is more than N hours ago",
        "is between N and M hours ago",
        "hours from now",
        "is less than N hours from now",
        "is more than N hours from now",
        "minutes ago",
        "is less than N minutes ago",
        "is more than N minutes ago",
        "is between N and M minutes ago",
        "minutes from now",
        "is less than N minutes from now",
        "is more than N minutes from now",
        "is null",
    },
    ListField: {
        "any",
        "contains",
        "contains (case-insensitive)",
        "is empty",
        "is not empty",
        "is of length",
        "is not of length",
        "is longer than",
        "is shorter than",
        "is longer than or equal to",
        "is shorter than or equal to",
        "contains all of",
        "contains all of (case-insensitive)",
        "contains N occurrences of",
        "contains at least N occurrences of",
        "contains at most N occurrences of",
        "contains any of",
        "contains any of (case-insensitive)",
        "contains none of",
        "contains none of (case-insensitive)",
        "does not contain",
        "does not contain (case-insensitive)",
        "is equal to",
        "is not equal to",
        "contains duplicates",
        "does not contain duplicates",
        "contains numbers in range (inclusive)",
        "contains object with key & value",
        "contains object with key & value (case-insensitive)",
        "does not contain object with key & value",
        "does not contain object with key & value (case-insensitive)",
        "contains object with key",
        "does not contain object with key",
        "contains only objects with keys",
        "does not contain only objects with keys",
        "contains object with data",
        "contains all objects with data",
        "does not contain object with data",
        "contains all elements in order",
        "contains all elements in order (case-insensitive)",
        "contains duplicates of value",
        "contains duplicates of value (case-insensitive)",
        "has unique elements",
        "is a sublist of",
        "is a superlist of",
        "has item at index",
        "has item at index (case-insensitive)",
        "does not have item at index",
        "does not have item at index (case-insensitive)",
        "has object with key & value at index",
        "has object with key & value at index (case-insensitive)",
        "object at index has keys",
        "contains any object with key",
        "is null",
    },
}

EXPECTED_OPERATOR_COUNTS = {
    BooleanField: 4,
    NumberField: 20,
    StringField: 59,
    DateField: 52,
    ListField: 54,
}

STRING_NEW_OPERATOR_CASES = [
    pytest.param("is_phone", (), "is a valid phone number", [], id="phone"),
    pytest.param("is_zip_code", (), "is a valid zip code", [], id="zip-code"),
    pytest.param("is_work_email", (), "is a work email address", [], id="work-email"),
    pytest.param(
        "is_personal_email",
        (),
        "is a personal email address",
        [],
        id="personal-email",
    ),
    pytest.param("is_ipv6", (), "is a valid IPV6 address", [], id="ipv6"),
    pytest.param(
        "is_not_ipv6",
        (),
        "is not a valid IPV6 address",
        [],
        id="not-ipv6",
    ),
    pytest.param(
        "is_credit_card",
        (),
        "is a valid credit card number",
        [],
        id="credit-card",
    ),
    pytest.param(
        "is_not_credit_card",
        (),
        "is not a valid credit card number",
        [],
        id="not-credit-card",
    ),
    pytest.param(
        "is_country_code",
        (),
        "is a valid country code",
        [],
        id="country-code",
    ),
    pytest.param(
        "is_not_country_code",
        (),
        "is not a valid country code",
        [],
        id="not-country-code",
    ),
    pytest.param(
        "contains_profanity",
        (),
        "contains profanity",
        [],
        id="contains-profanity",
    ),
    pytest.param(
        "does_not_contain_profanity",
        (),
        "does not contain profanity",
        [],
        id="not-profanity",
    ),
    pytest.param(
        "version_greater_than",
        ("1.2.3",),
        "version is greater than",
        ["1.2.3"],
        id="version-greater-than",
    ),
    pytest.param(
        "version_less_than",
        ("2.0.0",),
        "version is less than",
        ["2.0.0"],
        id="version-less-than",
    ),
    pytest.param(
        "version_equals",
        ("1.5.0",),
        "version is equal to",
        ["1.5.0"],
        id="version-equals",
    ),
    pytest.param(
        "version_greater_than_or_equal",
        ("1.2.3",),
        "version is greater than or equal to",
        ["1.2.3"],
        id="version-greater-than-or-equal",
    ),
    pytest.param(
        "version_less_than_or_equal",
        ("2.0.0",),
        "version is less than or equal to",
        ["2.0.0"],
        id="version-less-than-or-equal",
    ),
    pytest.param(
        "version_between",
        ("1.2.3", "2.0.0"),
        "version is between",
        ["1.2.3", "2.0.0"],
        id="version-between",
    ),
    pytest.param(
        "is_valid_semantic_version",
        (),
        "is valid semantic version",
        [],
        id="valid-semantic-version",
    ),
    pytest.param(
        "satisfies_version_range",
        ("^1.2.3",),
        "satisfies version range",
        ["^1.2.3"],
        id="satisfies-version-range",
    ),
]

DATE_NEW_OPERATOR_CASES = [
    pytest.param(
        "is_before_time",
        ("2:30 PM",),
        "is before time",
        ["2:30 PM"],
        id="before-time",
    ),
    pytest.param(
        "is_after_time",
        ("4:15 AM",),
        "is after time",
        ["4:15 AM"],
        id="after-time",
    ),
    pytest.param("hours_ago", (1,), "hours ago", [1], id="hours-ago"),
    pytest.param(
        "less_than_hours_ago",
        (2,),
        "is less than N hours ago",
        [2],
        id="less-than-hours-ago",
    ),
    pytest.param(
        "more_than_hours_ago",
        (3,),
        "is more than N hours ago",
        [3],
        id="more-than-hours-ago",
    ),
    pytest.param(
        "between_n_and_m_hours_ago",
        (4, 8),
        "is between N and M hours ago",
        [4, 8],
        id="between-hours-ago",
    ),
    pytest.param("hours_from_now", (5,), "hours from now", [5], id="hours-from-now"),
    pytest.param(
        "less_than_hours_from_now",
        (6,),
        "is less than N hours from now",
        [6],
        id="less-than-hours-from-now",
    ),
    pytest.param(
        "more_than_hours_from_now",
        (7,),
        "is more than N hours from now",
        [7],
        id="more-than-hours-from-now",
    ),
    pytest.param("minutes_ago", (10,), "minutes ago", [10], id="minutes-ago"),
    pytest.param(
        "less_than_minutes_ago",
        (11,),
        "is less than N minutes ago",
        [11],
        id="less-than-minutes-ago",
    ),
    pytest.param(
        "more_than_minutes_ago",
        (12,),
        "is more than N minutes ago",
        [12],
        id="more-than-minutes-ago",
    ),
    pytest.param(
        "between_n_and_m_minutes_ago",
        (13, 21),
        "is between N and M minutes ago",
        [13, 21],
        id="between-minutes-ago",
    ),
    pytest.param(
        "minutes_from_now",
        (14,),
        "minutes from now",
        [14],
        id="minutes-from-now",
    ),
    pytest.param(
        "less_than_minutes_from_now",
        (15,),
        "is less than N minutes from now",
        [15],
        id="less-than-minutes-from-now",
    ),
    pytest.param(
        "more_than_minutes_from_now",
        (16,),
        "is more than N minutes from now",
        [16],
        id="more-than-minutes-from-now",
    ),
]

LIST_NEW_OPERATOR_CASES = [
    pytest.param(
        "contains_case_insensitive",
        ("Alpha",),
        "contains (case-insensitive)",
        ["Alpha"],
        id="contains-case-insensitive",
    ),
    pytest.param(
        "longer_than_or_equal",
        (3,),
        "is longer than or equal to",
        [3],
        id="longer-than-or-equal",
    ),
    pytest.param(
        "shorter_than_or_equal",
        (9,),
        "is shorter than or equal to",
        [9],
        id="shorter-than-or-equal",
    ),
    pytest.param(
        "contains_all_case_insensitive",
        (["Alpha", 2],),
        "contains all of (case-insensitive)",
        [["Alpha", 2]],
        id="contains-all-case-insensitive",
    ),
    pytest.param(
        "contains_n_occurrences_of",
        ({"sku": "A"}, 2),
        "contains N occurrences of",
        [{"sku": "A"}, 2],
        id="contains-n-occurrences",
    ),
    pytest.param(
        "contains_at_least_n_occurrences_of",
        ("Alpha", 3),
        "contains at least N occurrences of",
        ["Alpha", 3],
        id="contains-at-least-n-occurrences",
    ),
    pytest.param(
        "contains_at_most_n_occurrences_of",
        (False, 4),
        "contains at most N occurrences of",
        [False, 4],
        id="contains-at-most-n-occurrences",
    ),
    pytest.param(
        "contains_any_case_insensitive",
        (["Alpha", 2],),
        "contains any of (case-insensitive)",
        [["Alpha", 2]],
        id="contains-any-case-insensitive",
    ),
    pytest.param(
        "contains_none_case_insensitive",
        (["Alpha", 2],),
        "contains none of (case-insensitive)",
        [["Alpha", 2]],
        id="contains-none-case-insensitive",
    ),
    pytest.param(
        "not_contains_case_insensitive",
        ("Alpha",),
        "does not contain (case-insensitive)",
        ["Alpha"],
        id="not-contains-case-insensitive",
    ),
    pytest.param(
        "contains_numbers_in_range",
        (1.5, 9),
        "contains numbers in range (inclusive)",
        [1.5, 9],
        id="contains-numbers-in-range",
    ),
    pytest.param(
        "contains_object_with_key_value_case_insensitive",
        ("status", "Open"),
        "contains object with key & value (case-insensitive)",
        ["status", "Open"],
        id="contains-object-key-value-case-insensitive",
    ),
    pytest.param(
        "does_not_contain_object_with_key_value_case_insensitive",
        ("status", "Closed"),
        "does not contain object with key & value (case-insensitive)",
        ["status", "Closed"],
        id="not-contains-object-key-value-case-insensitive",
    ),
    pytest.param(
        "contains_only_objects_with_keys",
        (["id", "name"],),
        "contains only objects with keys",
        [["id", "name"]],
        id="contains-only-objects-with-keys",
    ),
    pytest.param(
        "does_not_contain_only_objects_with_keys",
        (["id", "name"],),
        "does not contain only objects with keys",
        [["id", "name"]],
        id="not-contains-only-objects-with-keys",
    ),
    pytest.param(
        "contains_object_with_data",
        ({"profile": {"active": True}},),
        "contains object with data",
        [{"profile": {"active": True}}],
        id="contains-object-with-data",
    ),
    pytest.param(
        "contains_all_objects_with_data",
        ({"active": True},),
        "contains all objects with data",
        [{"active": True}],
        id="contains-all-objects-with-data",
    ),
    pytest.param(
        "does_not_contain_object_with_data",
        ({"archived": True},),
        "does not contain object with data",
        [{"archived": True}],
        id="not-contains-object-with-data",
    ),
    pytest.param(
        "contains_all_elements_in_order",
        (["Alpha", 2],),
        "contains all elements in order",
        [["Alpha", 2]],
        id="contains-all-elements-in-order",
    ),
    pytest.param(
        "contains_all_elements_in_order_case_insensitive",
        (["Alpha", 2],),
        "contains all elements in order (case-insensitive)",
        [["Alpha", 2]],
        id="contains-all-elements-in-order-case-insensitive",
    ),
    pytest.param(
        "contains_duplicates_of_value",
        ({"id": 1},),
        "contains duplicates of value",
        [{"id": 1}],
        id="contains-duplicates-of-value",
    ),
    pytest.param(
        "contains_duplicates_of_value_case_insensitive",
        ("Alpha",),
        "contains duplicates of value (case-insensitive)",
        ["Alpha"],
        id="contains-duplicates-of-value-case-insensitive",
    ),
    pytest.param(
        "has_item_at_index",
        (-1, {"sku": "A"}),
        "has item at index",
        [-1, {"sku": "A"}],
        id="has-item-at-index",
    ),
    pytest.param(
        "has_item_at_index_case_insensitive",
        (0, "Alpha"),
        "has item at index (case-insensitive)",
        [0, "Alpha"],
        id="has-item-at-index-case-insensitive",
    ),
    pytest.param(
        "does_not_have_item_at_index",
        (2, None),
        "does not have item at index",
        [2, None],
        id="not-has-item-at-index",
    ),
    pytest.param(
        "does_not_have_item_at_index_case_insensitive",
        (3, "Beta"),
        "does not have item at index (case-insensitive)",
        [3, "Beta"],
        id="not-has-item-at-index-case-insensitive",
    ),
    pytest.param(
        "has_object_with_key_value_at_index",
        (1, "status", "open"),
        "has object with key & value at index",
        [1, "status", "open"],
        id="has-object-key-value-at-index",
    ),
    pytest.param(
        "has_object_with_key_value_at_index_case_insensitive",
        (2, "status", "Open"),
        "has object with key & value at index (case-insensitive)",
        [2, "status", "Open"],
        id="has-object-key-value-at-index-case-insensitive",
    ),
    pytest.param(
        "object_at_index_has_keys",
        (-1, ["id", "name"]),
        "object at index has keys",
        [-1, ["id", "name"]],
        id="object-at-index-has-keys",
    ),
    pytest.param(
        "contains_any_object_with_key",
        ("id",),
        "contains any object with key",
        ["id"],
        id="contains-any-object-with-key",
    ),
]


@pytest.fixture(autouse=True)
def reset_vocabulary():
    Vocabulary._workspace = None
    Vocabulary.clear_cache()
    yield
    Vocabulary._workspace = None
    Vocabulary.clear_cache()


def make_workspace(rule_payload=None):
    rules = MagicMock()
    if rule_payload is not None:
        rules.pull.return_value = rule_payload
    workspace = SimpleNamespace(
        assets=SimpleNamespace(rules=rules),
        values=SimpleNamespace(list=MagicMock(), update=MagicMock()),
    )
    return workspace, rules


def test_published_snapshots_round_trip_and_are_omitted_when_absent():
    snapshots = {
        "published_requestSchema": [{"key": "published_input"}],
        "published_responseSchema": [{"key": "published_output"}],
        "published_conditions": [{"request": {}, "response": {}}],
        "published_groups": {"group-1": {"name": "Published"}},
    }

    hydrated = Rule.from_json(snapshots)
    serialized = hydrated.to_dict()

    assert serialized["published_requestSchema"] == snapshots["published_requestSchema"]
    assert serialized["published_responseSchema"] == snapshots["published_responseSchema"]
    assert serialized["published_conditions"] == snapshots["published_conditions"]
    assert serialized["published_groups"] == snapshots["published_groups"]

    ordinary_rule = Rule.from_json({})
    assert ordinary_rule.published_request_schema is None
    assert ordinary_rule.published_response_schema is None
    assert ordinary_rule.published_conditions is None
    assert ordinary_rule.published_groups is None
    assert PUBLISHED_KEYS.isdisjoint(ordinary_rule.to_dict())


def test_published_snapshot_camel_case_is_only_a_fallback():
    hydrated = Rule.from_json(
        {
            "published_requestSchema": [],
            "publishedRequestSchema": [{"key": "legacy"}],
            "publishedResponseSchema": [{"key": "legacy_response"}],
            "publishedConditions": [{"request": {}}],
            "publishedGroups": {"legacy": {}},
        }
    )

    assert hydrated.published_request_schema == []
    assert hydrated.published_response_schema == [{"key": "legacy_response"}]
    assert hydrated.published_conditions == [{"request": {}}]
    assert hydrated.published_groups == {"legacy": {}}
    assert hydrated.to_dict()["published_requestSchema"] == []


def test_response_date_and_list_fields_hydrate_under_schema_keys():
    hydrated = Rule.from_json(
        {
            "requestSchema": [
                {
                    "key": "requested_on",
                    "name": "Requested On",
                    "type": "date",
                    "defaultValue": "2026-08-19",
                }
            ],
            "responseSchema": [
                {
                    "key": "effective_on",
                    "name": "Effective On",
                    "type": "date",
                    "defaultValue": "2026-09-01",
                },
                {
                    "key": "eligible_plans",
                    "name": "Eligible Plans",
                    "type": "list",
                    "defaultValue": ["HSA"],
                },
            ],
        }
    )

    assert set(hydrated.request_fields) == {"requested_on"}
    assert set(hydrated.response_fields) == {"effective_on", "eligible_plans"}
    assert isinstance(hydrated.request_fields["requested_on"], DateField)
    assert isinstance(hydrated.response_fields["effective_on"], DateField)
    assert isinstance(hydrated.response_fields["eligible_plans"], ListField)
    serialized = hydrated.to_dict()
    assert serialized["requestSchema"][0]["name"] == "Requested On"
    assert serialized["responseSchema"][0]["name"] == "Effective On"

    missing_schemas = Rule.from_json(
        {"requestSchema": None, "responseSchema": None}
    )
    assert missing_schemas.request_fields == {}
    assert missing_schemas.response_fields == {}


def test_schema_metadata_opaque_fields_samples_and_top_level_metadata_round_trip():
    hydrated = Rule.from_json(
        {
            "id": "rule-id",
            "stable_id": "stable-rule-id",
            "labels": {"team": "risk"},
            "metadata": {"source": "migration"},
            "publishedAt": "2026-09-03T12:00:00.000Z",
            "requestSchema": [
                {
                    "key": "profile.score",
                    "name": "Score",
                    "type": "number",
                    "defaultValue": 0,
                    "show": False,
                    "valuesOnly": True,
                    "valuesPrefix": "Risk",
                    "extension": "preserved",
                },
                {
                    "key": "missing",
                    "name": "Missing",
                    "type": "number",
                    "defaultValue": 7,
                    "show": True,
                },
                {
                    "key": "payload",
                    "name": "Payload",
                    "type": "object",
                    "defaultValue": {},
                    "show": False,
                },
                {
                    "key": "formula",
                    "name": "Formula",
                    "type": "function",
                    "defaultValue": None,
                    "show": True,
                },
            ],
            "responseSchema": [
                {
                    "key": "approved",
                    "name": "Approved",
                    "type": "boolean",
                    "defaultValue": False,
                    "show": False,
                }
            ],
            "sampleRequest": {
                "profile": {"score": 42},
                "untouched": "value",
            },
            "sampleResponse": {"approved": True},
        }
    )

    serialized = hydrated.to_dict()
    assert serialized["stable_id"] == "stable-rule-id"
    assert serialized["labels"] == {"team": "risk"}
    assert serialized["metadata"] == {"source": "migration"}
    assert serialized["publishedAt"] == "2026-09-03T12:00:00.000Z"
    assert serialized["sampleRequest"] == {
        "profile": {"score": 42},
        "untouched": "value",
        "missing": 7,
        "payload": {},
        "formula": None,
    }
    assert serialized["sampleResponse"] == {"approved": True}
    score = next(
        field
        for field in serialized["requestSchema"]
        if field["key"] == "profile.score"
    )
    assert score["show"] is False
    assert score["valuesOnly"] is True
    assert score["valuesPrefix"] == "Risk"
    assert score["extension"] == "preserved"
    assert [field["type"] for field in serialized["requestSchema"]] == [
        "number",
        "number",
        "object",
        "function",
    ]
    assert serialized["responseSchema"][0]["show"] is False


def test_find_conditions_compares_values_structurally_and_vocabulary_by_id():
    rule = Rule.from_json(
        {
            "requestSchema": [
                {
                    "key": "score",
                    "name": "Score",
                    "type": "number",
                    "defaultValue": 0,
                    "show": True,
                }
            ],
            "responseSchema": [],
            "conditions": [
                {
                    "request": {
                        "score": {
                            "op": "equals",
                            "args": [
                                {
                                    "id": "value-id",
                                    "$rb": "globalValue",
                                    "name": "Old Name",
                                }
                            ],
                        }
                    },
                    "response": {},
                    "settings": {},
                },
                {
                    "request": {
                        "score": {
                            "op": "equals",
                            "args": [1],
                        }
                    },
                    "response": {},
                    "settings": {},
                },
            ],
        }
    )
    renamed_reference = VocabularyValue(
        "value-id",
        "New Name",
        VocabularyValueType.NUMBER,
    )

    assert len(
        rule.find_conditions(
            score=rule.get_number_field("score").equals(renamed_reference)
        )
    ) == 1
    assert rule.find_conditions(score=("equals", ["1"])) == []


def test_from_json_dumps_model_inputs_with_aliases():
    class ExportModel:
        def model_dump(self, *, by_alias=False):
            assert by_alias is True
            return {"requestSchema": [], "responseSchema": [], "name": "Aliased"}

    assert Rule.from_json(ExportModel()).name == "Aliased"


def test_from_workspace_retains_configured_client():
    workspace, _ = make_workspace({"id": "rule-id", "name": "Hydrated"})
    rule = Rule(workspace)

    hydrated = rule.from_workspace("rule-id")

    assert hydrated.workspace is workspace
    assert hydrated.name == "Hydrated"


@pytest.mark.parametrize(
    ("method_name", "should_publish"),
    [("update", False), ("publish", True)],
)
def test_update_and_publish_refresh_the_caller_in_place(
    method_name,
    should_publish,
):
    workspace, rules = make_workspace(
        {"id": "rule-id", "name": "Refreshed", "slug": "refreshed"}
    )
    rule = Rule(workspace)
    rule.id = "rule-id"
    original_identity = id(rule)

    returned = getattr(rule, method_name)()

    assert returned is rule
    assert id(rule) == original_identity
    assert rule.name == "Refreshed"
    assert rule.slug == "refreshed"
    assert rule.workspace is workspace
    pushed_rule = rules.push.call_args.kwargs["rule"]
    assert pushed_rule.get("_publish") is (True if should_publish else None)


def test_vocabulary_get_follows_pages_and_caches_exact_match():
    other = SimpleNamespace(id="other-id", name="target_suffix", type="string")
    target = SimpleNamespace(id="target-id", name="target", type="number")
    list_values = MagicMock(
        side_effect=[
            SimpleNamespace(data=[other], next_cursor="page-2"),
            SimpleNamespace(data=[target], next_cursor=None),
        ]
    )
    workspace = SimpleNamespace(values=SimpleNamespace(list=list_values))
    Vocabulary.configure(workspace)

    result = Vocabulary.get("target")

    assert result.id == "target-id"
    assert result.value_type == VocabularyValueType.NUMBER
    assert list_values.call_args_list == [
        call(name="target", limit=1000, cursor=None),
        call(name="target", limit=1000, cursor="page-2"),
    ]
    assert Vocabulary.get("target") is result
    assert list_values.call_count == 2


def test_vocabulary_get_supports_legacy_arrays_and_existing_errors():
    target = SimpleNamespace(id="target-id", name="target", type="string")
    list_values = MagicMock(return_value=[target])
    workspace = SimpleNamespace(values=SimpleNamespace(list=list_values))
    Vocabulary.configure(workspace)

    assert Vocabulary.get("target").id == "target-id"

    Vocabulary.clear_cache()
    list_values.return_value = []
    with pytest.raises(VocabularyValueNotFoundError):
        Vocabulary.get("missing")

    list_values.return_value = [
        SimpleNamespace(id="bad-id", name="bad", type="unsupported")
    ]
    with pytest.raises(ValueError, match="Invalid type 'unsupported'"):
        Vocabulary.get("bad")


def test_vocabulary_set_clears_cached_values():
    workspace = SimpleNamespace(
        values=SimpleNamespace(update=MagicMock())
    )
    Vocabulary.configure(workspace)
    Vocabulary._cache["stale"] = VocabularyValue(
        "stale-id",
        "stale",
        VocabularyValueType.STRING,
    )

    Vocabulary.set({"stale": "updated"})

    assert Vocabulary._cache == {}
    workspace.values.update.assert_called_once_with(
        values={"stale": "updated"},
        user_groups=[],
    )


@pytest.mark.parametrize(
    "literal",
    [
        "text",
        42,
        3.5,
        True,
        None,
        {"nested": "value"},
        ["nested", 1, False],
    ],
)
def test_list_generic_arguments_accept_json_literals(literal):
    _, args = ListField("items").contains(literal)

    assert args[0].to_dict() == literal


def test_list_generic_arguments_serialize_vocabulary_references():
    reference = VocabularyValue(
        "value-id",
        "allowed_value",
        VocabularyValueType.STRING,
    )
    field = ListField("items")

    _, contains_args = field.contains({"nested": [reference]})
    _, collection_args = field.contains_all(["literal", reference])

    assert contains_args[0].to_dict() == {
        "nested": [reference.to_dict()]
    }
    assert collection_args[0].to_dict() == [
        "literal",
        reference.to_dict(),
    ]


def test_list_generic_arguments_reject_non_payload_values_and_cycles():
    class CustomValue:
        pass

    field = ListField("items")
    cyclic = []
    cyclic.append(cyclic)

    with pytest.raises(TypeMismatchError, match="valid generic literal"):
        field.contains(CustomValue())
    with pytest.raises(TypeMismatchError, match="valid generic literal"):
        field.contains(float("nan"))
    with pytest.raises(TypeMismatchError, match="valid generic literal"):
        field.contains(cyclic)


def test_typed_arguments_remain_strict_for_list_object_and_function():
    with pytest.raises(TypeMismatchError):
        Argument("not-a-list", VocabularyValueType.LIST)
    with pytest.raises(TypeMismatchError):
        Argument(["not-an-object"], VocabularyValueType.OBJECT)
    with pytest.raises(TypeMismatchError):
        Argument("not-callable", VocabularyValueType.FUNCTION)

    assert Argument([], VocabularyValueType.LIST).to_dict() == []
    assert Argument({}, VocabularyValueType.OBJECT).to_dict() == {}
    function = lambda: None
    assert Argument(function, VocabularyValueType.FUNCTION).to_dict() is function


def test_date_arguments_accept_datetime_and_string_literals():
    field = DateField("effective_on")
    timestamp = datetime(2026, 8, 19, 12, 30)

    assert field.after(timestamp)[1][0].to_dict() == timestamp
    assert field.before("2026-09-01")[1][0].to_dict() == "2026-09-01"
    with pytest.raises(TypeMismatchError):
        field.equals(20260819)


def test_boolean_equals_only_accepts_literal_bool():
    field = BooleanField("enabled")
    reference = VocabularyValue(
        "boolean-id",
        "feature_enabled",
        VocabularyValueType.BOOLEAN,
    )

    assert field.equals(True) == ("is true", [])
    assert field.equals(False) == ("is false", [])
    with pytest.raises(TypeMismatchError, match="literal bool"):
        field.equals(reference)
    with pytest.raises(TypeMismatchError, match="literal bool"):
        field.equals(1)


@pytest.mark.parametrize(
    ("field_type", "expected_count"),
    [
        pytest.param(BooleanField, 4, id="boolean"),
        pytest.param(NumberField, 20, id="number"),
        pytest.param(StringField, 59, id="string"),
        pytest.param(DateField, 52, id="date"),
        pytest.param(ListField, 54, id="list"),
    ],
)
def test_operator_wire_name_catalog_is_exact(field_type, expected_count):
    expected_names = EXPECTED_OPERATOR_WIRE_NAMES[field_type]
    actual_names = [
        operator.name for operator in field_type("catalog_field").operators.values()
    ]

    assert expected_count == EXPECTED_OPERATOR_COUNTS[field_type]
    assert len(expected_names) == expected_count
    assert len(actual_names) == expected_count
    assert set(actual_names) == expected_names


def serialize_operator_call(field, method_name, method_args):
    operator, args = getattr(field, method_name)(*method_args)
    return operator, process_vocabulary_values(args)


@pytest.mark.parametrize(
    ("method_name", "method_args", "expected_operator", "expected_args"),
    STRING_NEW_OPERATOR_CASES,
)
def test_new_string_operator_emissions(
    method_name,
    method_args,
    expected_operator,
    expected_args,
):
    assert serialize_operator_call(
        StringField("text"),
        method_name,
        method_args,
    ) == (expected_operator, expected_args)


@pytest.mark.parametrize(
    ("method_name", "method_args", "expected_operator", "expected_args"),
    DATE_NEW_OPERATOR_CASES,
)
def test_new_date_operator_emissions(
    method_name,
    method_args,
    expected_operator,
    expected_args,
):
    assert serialize_operator_call(
        DateField("occurred_at"),
        method_name,
        method_args,
    ) == (expected_operator, expected_args)


@pytest.mark.parametrize(
    ("method_name", "method_args", "expected_operator", "expected_args"),
    LIST_NEW_OPERATOR_CASES,
)
def test_new_list_operator_emissions(
    method_name,
    method_args,
    expected_operator,
    expected_args,
):
    assert serialize_operator_call(
        ListField("items"),
        method_name,
        method_args,
    ) == (expected_operator, expected_args)


@pytest.mark.parametrize(
    (
        "field_type",
        "method_name",
        "expected_operator",
        "matching_type",
        "wrong_type",
    ),
    [
        pytest.param(
            StringField,
            "version_greater_than",
            "version is greater than",
            VocabularyValueType.STRING,
            VocabularyValueType.NUMBER,
            id="string",
        ),
        pytest.param(
            DateField,
            "hours_ago",
            "hours ago",
            VocabularyValueType.NUMBER,
            VocabularyValueType.STRING,
            id="number",
        ),
        pytest.param(
            ListField,
            "contains_all_case_insensitive",
            "contains all of (case-insensitive)",
            VocabularyValueType.LIST,
            VocabularyValueType.OBJECT,
            id="list",
        ),
        pytest.param(
            ListField,
            "contains_object_with_data",
            "contains object with data",
            VocabularyValueType.OBJECT,
            VocabularyValueType.LIST,
            id="object",
        ),
    ],
)
def test_typed_new_operators_accept_matching_vocabulary_and_reject_wrong_type(
    field_type,
    method_name,
    expected_operator,
    matching_type,
    wrong_type,
):
    matching_reference = VocabularyValue(
        f"{matching_type.value}-id",
        f"{matching_type.value}_value",
        matching_type,
    )
    wrong_reference = VocabularyValue(
        f"{wrong_type.value}-id",
        f"{wrong_type.value}_value",
        wrong_type,
    )
    field = field_type("field")

    assert serialize_operator_call(
        field,
        method_name,
        (matching_reference,),
    ) == (expected_operator, [matching_reference.to_dict()])

    with pytest.raises(TypeMismatchError, match=f"{matching_type.value} was expected"):
        getattr(field, method_name)(wrong_reference)


@pytest.mark.parametrize("value_type", list(VocabularyValueType))
def test_generic_new_operator_serializes_vocabulary_values_of_any_type(value_type):
    reference = VocabularyValue(
        f"{value_type.value}-id",
        f"{value_type.value}_value",
        value_type,
    )

    assert serialize_operator_call(
        ListField("items"),
        "contains_duplicates_of_value",
        (reference,),
    ) == ("contains duplicates of value", [reference.to_dict()])


def test_generic_new_operator_rejects_non_payload_shape():
    class UnsupportedValue:
        pass

    with pytest.raises(TypeMismatchError, match="valid generic literal"):
        ListField("items").contains_duplicates_of_value(UnsupportedValue())


@pytest.mark.parametrize(
    ("method_name", "expected_operator"),
    [
        pytest.param("is_included_in", "is included in", id="included-in"),
        pytest.param(
            "is_not_included_in",
            "is not included in",
            id="not-included-in",
        ),
        pytest.param("contains_any_of", "contains any of", id="contains-any"),
        pytest.param(
            "does_not_contain_any_of",
            "does not contain any of",
            id="does-not-contain-any",
        ),
    ],
)
def test_string_collection_operators_serialize_mixed_literal_and_vocabulary_values(
    method_name,
    expected_operator,
):
    reference = VocabularyValue(
        "string-id",
        "allowed_text",
        VocabularyValueType.STRING,
    )

    assert serialize_operator_call(
        StringField("text"),
        method_name,
        (["literal", reference],),
    ) == (expected_operator, [["literal", reference.to_dict()]])


@pytest.mark.parametrize(
    "method_name",
    [
        "is_included_in",
        "is_not_included_in",
        "contains_any_of",
        "does_not_contain_any_of",
    ],
)
def test_string_collection_operators_reject_wrong_typed_vocabulary_items(
    method_name,
):
    wrong_reference = VocabularyValue(
        "number-id",
        "numeric_value",
        VocabularyValueType.NUMBER,
    )

    with pytest.raises(TypeMismatchError, match="string was expected"):
        getattr(StringField("text"), method_name)(["literal", wrong_reference])


@pytest.mark.parametrize(
    ("method_name", "method_args"),
    [
        pytest.param("version_greater_than", ("",), id="greater-than"),
        pytest.param("version_less_than", ("",), id="less-than"),
        pytest.param("version_equals", ("",), id="equals"),
        pytest.param(
            "version_greater_than_or_equal",
            ("",),
            id="greater-than-or-equal",
        ),
        pytest.param(
            "version_less_than_or_equal",
            ("",),
            id="less-than-or-equal",
        ),
        pytest.param(
            "version_between",
            ("", "2.0.0"),
            id="between-empty-minimum",
        ),
        pytest.param(
            "version_between",
            ("1.0.0", ""),
            id="between-empty-maximum",
        ),
        pytest.param("satisfies_version_range", ("",), id="range"),
    ],
)
def test_string_version_operators_reject_empty_literals(method_name, method_args):
    with pytest.raises(ValueError):
        getattr(StringField("version"), method_name)(*method_args)


@pytest.mark.parametrize(
    "method_name",
    [
        "length_equals",
        "length_not_equals",
        "longer_than",
        "shorter_than",
        "longer_than_or_equal",
        "shorter_than_or_equal",
    ],
)
def test_string_length_operators_reject_zero(method_name):
    with pytest.raises(ValueError):
        getattr(StringField("text"), method_name)(0)


@pytest.mark.parametrize("base", [0, -2])
def test_number_is_power_of_allows_nonpositive_literals_at_construction(base):
    assert serialize_operator_call(
        NumberField("value"),
        "is_power_of",
        (base,),
    ) == ("is a power of", [base])


@pytest.mark.parametrize("method_name", ["between", "not_between"])
def test_number_range_validation_is_retained(method_name):
    field = NumberField("value")

    assert serialize_operator_call(field, method_name, (1, 2)) == (
        method_name.replace("_", " "),
        [1, 2],
    )
    with pytest.raises(ValueError, match="start .* must be less than end"):
        getattr(field, method_name)(2, 2)
    with pytest.raises(ValueError, match="start .* must be less than end"):
        getattr(field, method_name)(3, 2)


def test_number_collection_membership_serializes_and_validates_entries():
    field = NumberField("value")
    number_reference = VocabularyValue(
        "number-id",
        "Allowed.Number",
        VocabularyValueType.NUMBER,
    )
    list_reference = VocabularyValue(
        "list-id",
        "Allowed.Numbers",
        VocabularyValueType.LIST,
    )

    assert serialize_operator_call(
        field,
        "is_included_in",
        ([1, number_reference],),
    ) == ("is included in", [[1, number_reference.to_dict()]])
    assert serialize_operator_call(
        field,
        "is_included_in",
        (list_reference,),
    ) == ("is included in", [list_reference.to_dict()])
    with pytest.raises(ValueError, match="at least one value"):
        field.is_included_in([])
    with pytest.raises(TypeMismatchError, match="number was expected"):
        field.is_included_in(
            [
                VocabularyValue(
                    "string-id",
                    "Wrong",
                    VocabularyValueType.STRING,
                )
            ]
        )


@pytest.mark.parametrize(
    "value",
    [
        pytest.param(float("nan"), id="nan"),
        pytest.param(float("inf"), id="positive-infinity"),
        pytest.param(float("-inf"), id="negative-infinity"),
    ],
)
def test_typed_number_arguments_reject_nonfinite_values(value):
    with pytest.raises(TypeMismatchError, match="number was expected"):
        Argument(value, VocabularyValueType.NUMBER)


def make_deep_invalid_value(expected_type, invalid_shape):
    if invalid_shape == "nonfinite":
        if expected_type == VocabularyValueType.LIST:
            return [{"nested": [float("nan")]}]
        return {"nested": [float("inf")]}

    if invalid_shape == "unsupported":
        if expected_type == VocabularyValueType.LIST:
            return [{"nested": [object()]}]
        return {"nested": [object()]}

    if invalid_shape == "cycle":
        if expected_type == VocabularyValueType.LIST:
            cyclic_list = []
            cyclic_list.append(cyclic_list)
            return cyclic_list
        cyclic_object = {}
        cyclic_object["self"] = cyclic_object
        return cyclic_object

    if expected_type == VocabularyValueType.LIST:
        return [{"nested": {1: "non-string key"}}]
    return {"nested": {1: "non-string key"}}


@pytest.mark.parametrize(
    "expected_type",
    [VocabularyValueType.LIST, VocabularyValueType.OBJECT],
)
@pytest.mark.parametrize(
    "invalid_shape",
    ["nonfinite", "unsupported", "cycle", "non-string-key"],
)
def test_typed_collection_arguments_reject_deep_invalid_values(
    expected_type,
    invalid_shape,
):
    with pytest.raises(TypeMismatchError):
        Argument(
            make_deep_invalid_value(expected_type, invalid_shape),
            expected_type,
        )


def test_rule_when_then_serializes_new_operator_payload():
    rule = Rule()
    items = rule.add_list_field("items")
    rule.add_boolean_response("matched")

    rule.when(
        items=items.has_object_with_key_value_at_index(
            0,
            "status",
            "active",
        )
    ).then(matched=True)

    assert rule.conditions[0]["request"]["items"] == {
        "op": "has object with key & value at index",
        "args": [0, "status", "active"],
    }
