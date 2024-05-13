# pyefergy

[![codecov](https://codecov.io/gh/tkdrob/pyefergy/branch/master/graph/badge.svg)](https://codecov.io/gh/tkdrob/pyefergy)
![python version](https://img.shields.io/badge/Python-3.8=><=3.12-blue.svg)
[![PyPI](https://img.shields.io/pypi/v/pyefergy)](https://pypi.org/project/pyefergy)
![Actions](https://github.com/tkdrob/pyefergy/workflows/Actions/badge.svg?branch=master)

_Python API client for Efergy._

## Installation

```bash
python3 -m pip install pyefergy
```

## Example usage

More examples can be found in the `tests` directory.

```python
"""Example usage of pyefergy."""
import asyncio
from pyefergy import Efergy

TOKEN = "xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
OFFSET = "America/New_York"  # Accepts either a time zone or literal offset


async def async_example():
    """Example usage of pyefergy."""
    api = Efergy(TOKEN, utc_offset=OFFSET)
    async with api:
        print(await api.async_get_reading("instant_readings"))

asyncio.get_event_loop().run_until_complete(async_example())
```

## Contribute

**All** contributions are welcome!

1. Fork the repository
2. Clone the repository locally and open the devcontainer or use GitHub codespaces
3. Install poetry
4. Install dependencies: `poetry install`
5. Do your changes
6. Lint the files with `poetry run pylint pyefergy && black . && ruff check && mypy pyefergy`
7. Ensure all tests pass with `poetry run pytest`
8. Ensure 100% coverage
9. Commit your work, and push it to GitHub
10. Create a PR against the `master` branch