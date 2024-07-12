# Rulebricks – Python SDK

[![pypi](https://img.shields.io/pypi/v/rulebricks.svg)](https://pypi.python.org/pypi/rulebricks)

The Rulebricks Python SDK provides convenient access to the Rulebricks API from Python.

## Documentation

API reference documentation is available [here](https://rulebricks.com/docs).

## Installation

Add this dependency to your project's build file:

```bash
pip install rulebricks
# or
poetry add rulebricks
```

## Configuration

Before using the SDK, configure your API key. You can find your API key in your Rulebricks Dashboard.

```python
import rulebricks as rb

# Replace 'XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX' with your actual API key
rb.configure(
    api_key="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    # base_url="https://rulebricks.com" # Optional: Use this to override the default base URL for private cloud deployments
    # timeout=10 # Optional: Use this to override the default timeout in seconds
)
```

## Basic Usage

Using the SDK to interact with the Rulebricks API in a synchronous manner is simple.

Here's an example of how to use our Python SDK to solve a rule:

```python
import rulebricks as rb

# Set the API key
rb.configure(
    api_key="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
)

result = rb.rules.solve(
    slug="tJOCd8XXXX",
    request={
        "customer_id": "anc39as3",
        "purchase_history": ["t-shirt", "mug"],
        "account_age_days": 4,
        "last_purchase_days_ago": 3,
        "email_subscription": False
    }
)

print(result)
```

## Asynchronous Usage

For asynchronous API calls, access methods via the async_api attribute.

This allows you to leverage Python's asyncio library for non-blocking operations:

```python
import rulebricks as rb
import asyncio

# Set the API key
rb.configure(
    api_key="XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
)

async def main():
    async_result = await rb.async_api.rules.solve(
        slug="tJOCd8XXXX",
        request={
            "customer_id": "anc39as3",
            "purchase_history": ["t-shirt", "mug"],
            "account_age_days": 4,
            "last_purchase_days_ago": 3,
            "email_subscription": False
        }
    )
    print(async_result)

if __name__ == "__main__":
    asyncio.run(main())
```

Using a combination of `solve`, `bulk_solve`, `parallel_solve` and `flows` in synchronous or asynchronous modes gives you high flexibility to interact with the Rulebricks API in a way that best suits your application's needs.

## Forge SDK

The Forge SDK is a powerful tool within the Rulebricks package that allows you to programmatically create and manage rules. It provides a flexible and intuitive way to define rule sets, conditions, and responses.

### Purpose

The Forge SDK enables you to:
- Define complex rule structures
- Create and manage conditions within rules
- Specify request and response schemas
- Generate rule representations in various formats (JSON, tabular, file)

### Creating a Rule

Here's an example of how to create a simple rule using the Forge SDK:

```python
from rulebricks import RuleBuilder, RuleType
from rulebricks.forge import BooleanOperator, NumberOperator, StringOperator, boolean_op, number_op, string_op

# Initialize a new RuleBuilder
builder = RuleBuilder()

# Set name and description
builder.set_name("Customer Discount Eligibility")
builder.set_description("Determines if a customer is eligible for a discount based on their purchase history and account status.")

# Define schema
builder.add_request_field("purchase_count", "Purchase Count", RuleType.NUMBER, "Number of purchases made", 0)
builder.add_request_field("is_subscribed", "Is Subscribed", RuleType.BOOLEAN, "Whether the customer is subscribed to the newsletter", False)
builder.add_request_field("customer_type", "Customer Type", RuleType.STRING, "Type of customer (regular, premium, vip)", "regular")

builder.add_response_field("discount_eligible", "Discount Eligible", RuleType.BOOLEAN, "Whether the customer is eligible for a discount", False)
builder.add_response_field("discount_percentage", "Discount Percentage", RuleType.NUMBER, "Percentage of discount to apply", 0)

# Create conditions
condition1 = builder.add_condition()
builder.update_condition(condition1, "purchase_count", *number_op(NumberOperator.GREATER_THAN_OR_EQUAL_TO)(10))
builder.update_condition(condition1, "is_subscribed", *boolean_op(BooleanOperator.IS_TRUE)())
builder.update_condition(condition1, "customer_type", *string_op(StringOperator.EQUALS)("regular"))
builder.set_condition_response(condition1, "discount_eligible", True)
builder.set_condition_response(condition1, "discount_percentage", 5)

condition2 = builder.add_condition()
builder.update_condition(condition2, "customer_type", *string_op(StringOperator.EQUALS)("premium"))
builder.set_condition_response(condition2, "discount_eligible", True)
builder.set_condition_response(condition2, "discount_percentage", 10)
```

### Available Operators

The Forge SDK provides a range of operators for different data types. You can find the full list of available operators in the following files:

- `src/rulebricks/forge/operators.py`

This file contains the definitions for `BooleanOperator`, `NumberOperator`, `StringOperator`, `DateOperator`, and `ListOperator`.

### Outputting Rules

The Forge SDK offers several ways to output your rules:

1. **JSON Output**

   To get a JSON representation of your rule:

   ```python
   json_output = builder.to_json()
   print(json_output)
   ```

2. **Pretty Print (Tabular Format)**

   To get a human-readable tabular representation of your rule:

   ```python
   table_output = builder.to_table()
   print(table_output)
   ```

   This might produce output similar to:

   ```
   +---------------+---------------+-----------------+-------------------+----------------------+
   | purchase_count | is_subscribed |  customer_type  | discount_eligible | discount_percentage  |
   +===============+===============+=================+===================+======================+
   | greater than   | is true       | equals          | True              | 5                    |
   | or equal to    | ()            | (regular)       |                   |                      |
   | (10)           |               |                 |                   |                      |
   +---------------+---------------+-----------------+-------------------+----------------------+
   | -              | -             | equals          | True              | 10                   |
   |                |               | (premium)       |                   |                      |
   +---------------+---------------+-----------------+-------------------+----------------------+
   ```

3. **Export to File**

   To export your rule to a file for import through the Rulebricks UI:

   ```python
   filename = builder.export()
   print(f"Rule exported to: {filename}")
   ```

   This will create a file with the `.rbx` extension in your current directory. The filename will be based on the rule name you set, with "-Generated.rbx" appended.

### Complete Example

Here's a complete example that demonstrates creating a rule and using all output methods:

```python
from rulebricks import RuleBuilder, RuleType
from rulebricks.forge import BooleanOperator, NumberOperator, StringOperator, boolean_op, number_op, string_op

def create_customer_discount_rule():
    builder = RuleBuilder()

    builder.set_name("Customer Discount Eligibility")
    builder.set_description("Determines if a customer is eligible for a discount based on their purchase history and account status.")

    builder.add_request_field("purchase_count", "Purchase Count", RuleType.NUMBER, "Number of purchases made", 0)
    builder.add_request_field("is_subscribed", "Is Subscribed", RuleType.BOOLEAN, "Whether the customer is subscribed to the newsletter", False)
    builder.add_request_field("customer_type", "Customer Type", RuleType.STRING, "Type of customer (regular, premium, vip)", "regular")

    builder.add_response_field("discount_eligible", "Discount Eligible", RuleType.BOOLEAN, "Whether the customer is eligible for a discount", False)
    builder.add_response_field("discount_percentage", "Discount Percentage", RuleType.NUMBER, "Percentage of discount to apply", 0)

    condition1 = builder.add_condition()
    builder.update_condition(condition1, "purchase_count", *number_op(NumberOperator.GREATER_THAN_OR_EQUAL_TO)(10))
    builder.update_condition(condition1, "is_subscribed", *boolean_op(BooleanOperator.IS_TRUE)())
    builder.update_condition(condition1, "customer_type", *string_op(StringOperator.EQUALS)("regular"))
    builder.set_condition_response(condition1, "discount_eligible", True)
    builder.set_condition_response(condition1, "discount_percentage", 5)

    condition2 = builder.add_condition()
    builder.update_condition(condition2, "customer_type", *string_op(StringOperator.EQUALS)("premium"))
    builder.set_condition_response(condition2, "discount_eligible", True)
    builder.set_condition_response(condition2, "discount_percentage", 10)

    return builder

if __name__ == "__main__":
    rule = create_customer_discount_rule()

    # JSON output
    print("JSON Output:")
    print(rule.to_json())
    print("\n")

    # Table output
    print("Table Output:")
    print(rule.to_table())
    print("\n")

    # Export to file
    filename = rule.export()
    print(f"Rule exported to: {filename}")
```

## Feedback and Contributions

Feedback is vital as we continue to improve the SDK and add more features. Please report any issues or suggest improvements through our GitHub issues page. Contributions to the SDK are welcome via pull requests.
