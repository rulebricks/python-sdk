# Rulebricks Python Library

## Documentation

API reference documentation is available [here](https://rulebricks.com/docs).

## Installation

Add this dependency to your project's build file:

```bash
pip install rulebricks
# or
poetry add rulebricks
```

## Usage

```python
import rulebricks as rb

# Find your API key at https://rulebricks.com/dashboard and replace it below
rb.set_api_key("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

result = rb.rules.solve(
    slug="tJOCd8XXXX",
    request={
        "customer_id": "anc39as3",
        "purchase_history": [
            "t-shirt",
            "mug",
        ],
        "account_age_days": 4,
        "last_purchase_days_ago": 3,
        "email_subscription": False
    }
)

print(result)
```

## Async Usage

```python
import rulebricks as rb
import asyncio

# Set the API key
rb.set_api_key("XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX")

async def main():
    async_result = await rb.async.solve(
        slug="tJOCd8XXXX",
        request={
            "customer_id": "anc39as3",
            "purchase_history": [
                "t-shirt",
                "mug",
            ],
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
