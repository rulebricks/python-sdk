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
from rulebricks.client import Rulebricks

rulebricks_client = Rulebricks(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
```

## Async Client

```python
from rulebricks.client import AsyncFlatFile
import flatfile

import asyncio

rulebricks_client = AsyncRulebricks(
    api_key="YOUR_API_KEY",
    base_url="https://yourhost.com/path/to/api",
)
```

## Beta status

This SDK is in beta, and there may be breaking changes between versions without a major version update. Therefore, we recommend pinning the package version to a specific version in your pyproject.toml file. This way, you can install the same version each time without breaking changes unless you are intentionally looking for the latest version.
