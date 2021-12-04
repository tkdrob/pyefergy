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