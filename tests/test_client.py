import ast
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


def _type_checking_names() -> set:
    """Names the package advertises to type checkers via `if TYPE_CHECKING:`."""
    tree = ast.parse(Path(rulebricks.__file__).read_text())
    names = set()
    for node in tree.body:
        if not isinstance(node, ast.If):
            continue
        test = node.test
        is_type_checking = (isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING") or (
            isinstance(test, ast.Name) and test.id == "TYPE_CHECKING"
        )
        if not is_type_checking:
            continue
        for statement in node.body:
            assert isinstance(statement, ast.ImportFrom)
            names.update(alias.asname or alias.name for alias in statement.names)
    return names


def test_type_checking_exports_match_runtime_exports() -> None:
    # What Pylance/pyright autocompletes must be what `from rulebricks import X` returns at runtime.
    type_checking_names = _type_checking_names()
    assert type_checking_names
    assert type_checking_names == set(rulebricks._dynamic_imports)
    assert type_checking_names == set(rulebricks.__all__)
    for name in sorted(type_checking_names):
        assert getattr(rulebricks, name) is not None


def test_forge_is_importable_from_package_root() -> None:
    from rulebricks import Condition, Rule, Vocabulary, VocabularyValue
    from rulebricks import forge

    assert Rule is forge.Rule
    assert Condition is forge.Condition
    assert Vocabulary is forge.Vocabulary
    assert VocabularyValue is forge.VocabularyValue


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