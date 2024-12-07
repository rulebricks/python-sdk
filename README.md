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

## Full SDK Example

A particularly comprehensive example of using the Rulebricks Python SDK can be found in the [src/rulebricks/forge/examples/health_insurance_selector.py](src/rulebricks/forge/examples/health_insurance_selector.py) file.

This example programmatically constructs a rule, visualizes it locally, syncs it with a Rulebricks workspace, and solves the rule with a sample request.

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
- Define complex and large rule structures
- Create and manage conditions within rules
- Specify request and response schemas
- Generate rule representations in various formats (JSON, tabular, file)

### Creating a Rule

Here's a simple example of creating a rule:

```python
from rulebricks.forge import Rule

# Initialize a new rule
rule = Rule()

# Set basic metadata
rule.set_name("Customer Discount Rule") \
    .set_description("Determines customer discount eligibility based on purchase history")

# Define fields
purchase_count = rule.add_number_field("purchase_count", "Number of purchases", 0)
is_subscribed = rule.add_boolean_field("is_subscribed", "Newsletter subscription status", False)
customer_type = rule.add_string_field("customer_type", "Customer type", "regular")

# Define response fields
# Note we do not create variables for response fields
rule.add_boolean_response("discount_eligible", "Discount eligibility", False)
rule.add_number_response("discount_amount", "Discount percentage", 0)

# Add conditions
# By default, conditions are ANDed together
rule.when(
    purchase_count=purchase_count.greater_than(10), # "...and "
    is_subscribed=is_subscribed.equals(True), # "...and "
    customer_type=customer_type.equals("regular")
).then(
    discount_eligible=True,
    discount_amount=5
)

# Or, you can use `any` to OR your conditions
# rule.any(
#     purchase_count=purchase_count.less_than(10),
#     is_subscribed=is_subscribed.equals(False),
# ).then(
#     discount_eligible=False
# )

# Export the rule
rule.export()
```

### Field Types

These operators match the ones available to you when defining conditions in the Rulebricks decision table editor.
We are always adding more operators, so the lists below likely will not be exhaustive.

#### Boolean Fields

Boolean fields support these operations:

```python
boolean_field = rule.add_boolean_field("field_name")
boolean_field.equals(True)    # Check if true
boolean_field.equals(False)   # Check if false
boolean_field.any()           # Match any value
```

#### Number Fields

Number fields support these operations:

```python
number_field = rule.add_number_field("field_name")
number_field.equals(value)                    # Exact match
number_field.not_equals(value)                # Not equal to
number_field.greater_than(value)              # Greater than
number_field.less_than(value)                 # Less than
number_field.greater_than_or_equal(value)     # Greater than or equal to
number_field.less_than_or_equal(value)        # Less than or equal to
number_field.between(start, end)              # Between two values (inclusive)
number_field.not_between(start, end)          # Not between two values
number_field.is_even()                        # Check if even
number_field.is_odd()                         # Check if odd
number_field.is_positive()                    # Check if positive
number_field.is_negative()                    # Check if negative
number_field.is_zero()                        # Check if zero
number_field.is_not_zero()                    # Check if not zero
number_field.is_multiple_of(value)            # Check if multiple of value
number_field.is_not_multiple_of(value)        # Check if not multiple of value
number_field.is_power_of(base)                # Check if power of base
```

#### String Fields

String fields support these operations:

```python
string_field = rule.add_string_field("field_name")
string_field.contains(value)                # Contains substring
string_field.not_contains(value)            # Does not contain substring
string_field.equals(value)                  # Exact match
string_field.not_equals(value)              # Not equal to
string_field.is_empty()                     # Check if empty
string_field.is_not_empty()                 # Check if not empty
string_field.starts_with(value)             # Starts with prefix
string_field.ends_with(value)               # Ends with suffix
string_field.is_included_in(list)           # Value is in list
string_field.is_not_included_in(list)       # Value is not in list
string_field.contains_any_of(list)          # Contains any value from list
string_field.not_contains_any_of(list)      # Contains none from list
string_field.matches_regex(pattern)         # Matches regex pattern
string_field.not_matches_regex(pattern)     # Does not match regex
string_field.is_email()                     # Is valid email
string_field.is_not_email()                 # Is not valid email
string_field.is_url()                       # Is valid URL
string_field.is_not_url()                   # Is not valid URL
string_field.is_ip()                        # Is valid IP address
string_field.is_not_ip()                    # Is not valid IP address
```

#### Date Fields

Date fields support these operations:

```python
date_field = rule.add_date_field("field_name")
date_field.is_past()                        # Date is in the past
date_field.is_future()                      # Date is in the future
date_field.days_ago(days)                   # Exact number of days ago
date_field.less_than_days_ago(days)         # Less than N days ago
date_field.more_than_days_ago(days)         # More than N days ago
date_field.days_from_now(days)              # Exact number of days from now
date_field.less_than_days_from_now(days)    # Less than N days from now
date_field.more_than_days_from_now(days)    # More than N days from now
date_field.is_today()                       # Is today
date_field.is_this_week()                   # Is this week
date_field.is_this_month()                  # Is this month
date_field.is_this_year()                   # Is this year
date_field.after(date)                      # After date
date_field.on_or_after(date)                # On or after date
date_field.before(date)                     # Before date
date_field.on_or_before(date)               # On or before date
date_field.between(start, end)              # Between two dates
date_field.not_between(start, end)          # Not between two dates
```

#### List Fields

List fields support these operations:

```python
list_field = rule.add_list_field("field_name")
list_field.contains(value)                  # Contains value
list_field.is_empty()                       # Is empty list
list_field.is_not_empty()                   # Is not empty
list_field.length_equals(length)            # Has exact length
list_field.length_not_equals(length)        # Does not have length
list_field.longer_than(length)              # Longer than length
list_field.shorter_than(length)             # Shorter than length
list_field.contains_all(values)             # Contains all values
list_field.contains_any(values)             # Contains any value
list_field.contains_none(values)            # Contains none of values
list_field.equals(other)                    # Equals another list
list_field.not_equals(other)                # Not equal to list
list_field.has_duplicates()                 # Has duplicate values
list_field.no_duplicates()                  # Has no duplicates
```

### Rule Operations

#### Exporting Rules

Rules can be exported to files:

```python
# Export with default filename
filename = rule.export()

# Export to specific directory
filename = rule.export(directory="/path/to/directory")
```

#### JSON Conversion

Rules can be converted to and from JSON format:

```python
# Convert rule to JSON string
json_str = rule.to_json()

# Convert rule to dictionary
dict_data = rule.to_dict()

# Create rule from JSON string
rule = Rule.from_json(json_str)

# Create rule from dictionary
rule = Rule.from_json(dict_data)
```

The `from_json` method accepts either a JSON string or a dictionary and will reconstruct the entire rule, including:
- Basic metadata (name, description, etc.)
- Request and response schemas
- All conditions and their operators
- Field definitions and types

#### Tabular Visualization

Rules can be visualized in a table format using the `to_table()` method:

```python
# Print rule in table format
print(rule.to_table())
```

This will produce a grid-formatted table showing all conditions and their corresponding responses:

```
+---------------+---------------+-----------------+-------------------+
| age           | income        | customer_type   | discount          |
+===============+===============+=================+===================+
| greater than  | between       | equals          | 20                |
| (30)          | (50000,      | (premium)       |                   |
|               | 100000)       |                 |                   |
+---------------+---------------+-----------------+-------------------+
| less than     | greater than  | equals          | 10                |
| (30)          | (30000)       | (standard)      |                   |
+---------------+---------------+-----------------+-------------------+
```

The table format makes it easy to:
- Visualize all conditions at once
- Compare different conditions
- Verify rule logic
- Share rule definitions with stakeholders

### Best Practices

1. **Field References**: Store field references in variables when you need to use them multiple times:
   ```python
   age = rule.add_number_field("age")
   # Use age variable in multiple conditions
   ```

2. **Chaining**: Use method chaining for cleaner code:
   ```python
   rule.set_name("My Rule").set_description("Description")
   ```

3. **Condition Organization**: Group related conditions together:
   ```python
   # Premium customer condition
   rule.when(
       customer_type=customer_type.equals("premium"),
       purchase_count=purchase_count.greater_than(100)
   ).then(
       discount=20
   )
   ```

4. **Meaningful Names**: Use descriptive names for fields and rules:
   ```python
   # Good
   purchase_history = rule.add_list_field("purchase_history")

   # Not as clear
   ph = rule.add_list_field("ph")
   ```

### Migration Guide

If you're migrating from the old interface:

Old interface:
```python
builder.update_condition(condition, "age", *number_op(NumberOperator.GREATER_THAN_OR_EQUAL_TO)(10))
```

New interface:
```python
age = rule.add_number_field("age")
rule.when(age=age.greater_than_or_equal(10)).then(...)
```

The new SDK is easier to read, requires less code, and provides a better developer experience in modern IDEs.

## Feedback and Contributions

Feedback is vital as we continue to improve the SDK and add more features. Please report any issues or suggest improvements through our GitHub issues page. Contributions to the SDK are welcome via pull requests.
