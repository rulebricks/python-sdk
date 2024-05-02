# Rulebricks – Python SDK

[![pypi](https://img.shields.io/pypi/v/flatfile.svg)](https://pypi.python.org/pypi/rulebricks)

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
rb.set_api_key("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")
```

## Basic Usage

Use the SDK to interact with the Rulebricks API in a synchronous manner is incredibly simple.

Here's an example of how to use the SDK to solve a rule:

```python
import rulebricks as rb

# Set the API key
rb.set_api_key("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

result = rb.sync_api.rules.solve(
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
rb.set_api_key("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

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

## Beta status

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning the package version to a specific version in your pyproject.toml file. This way, you can install the same version each time without breaking changes unless you are intentionally looking for the latest version.

## Feedback and Contributions

Feedback is vital as we continue to improve the SDK and add more features. Please report any issues or suggest improvements through our GitHub issues page. Contributions to the SDK are welcome via pull requests.
