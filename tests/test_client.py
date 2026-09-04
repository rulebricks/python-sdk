import inspect
from pathlib import Path

import rulebricks
from rulebricks.assets.client import AssetsClient, AsyncAssetsClient
from rulebricks.assets.contexts.client import AsyncContextsClient, ContextsClient
from rulebricks.client import AsyncRulebricks, Rulebricks
from rulebricks.tests.client import AsyncTestsClient as AsyncRuleTestsClient
from rulebricks.tests.client import TestsClient as RuleTestsClient
from rulebricks.users.client import AsyncUsersClient, UsersClient


def test_package_declares_inline_types() -> None:
    assert Path(rulebricks.__file__).with_name("py.typed").is_file()


def test_resource_properties_expose_return_types() -> None:
    resource_properties = {
        Rulebricks: (
            "rules",
            "infra",
            "flows",
            "decisions",
            "users",
            "assets",
            "values",
            "objects",
            "contexts",
            "tests",
        ),
        AsyncRulebricks: (
            "rules",
            "infra",
            "flows",
            "decisions",
            "users",
            "assets",
            "values",
            "objects",
            "contexts",
            "tests",
        ),
        AssetsClient: ("rules", "flows", "folders", "contexts"),
        AsyncAssetsClient: ("rules", "flows", "folders", "contexts"),
        ContextsClient: ("relationships",),
        AsyncContextsClient: ("relationships",),
        RuleTestsClient: ("rules", "flows"),
        AsyncRuleTestsClient: ("rules", "flows"),
        UsersClient: ("groups",),
        AsyncUsersClient: ("groups",),
    }

    for client_type, property_names in resource_properties.items():
        for property_name in property_names:
            resource_property = getattr(client_type, property_name)
            assert isinstance(resource_property, property)
            assert resource_property.fget is not None
            assert inspect.signature(resource_property.fget).return_annotation is not inspect.Signature.empty