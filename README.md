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

## Feedback and Contributions

Feedback is vital as we continue to improve the SDK and add more features. Please report any issues or suggest improvements through our GitHub issues page. Contributions to the SDK are welcome via pull requests.
