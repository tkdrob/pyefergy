"""Tests configuration."""
# pylint:disable=redefined-outer-name
import asyncio

from aiohttp import ClientSession
from pyefergy import Efergy
import pytest

from tests import API_KEY


@pytest.fixture(autouse=True)
def loop_factory():
    """Create loop."""
    return asyncio.new_event_loop


@pytest.fixture()
async def apisession():
    """Create client session."""
    async with ClientSession() as sess:
        yield sess


@pytest.fixture()
async def client(apisession):
    """Create Client."""
    async with Efergy(API_KEY, session=apisession, utc_offset="America/New_York", currency="USD") as obj:
        yield obj
