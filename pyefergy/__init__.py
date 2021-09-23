"""An API library for efergy energy meters."""
from __future__ import annotations
from typing import Any
import logging
from aiohttp import ClientSession
from asyncio.exceptions import TimeoutError as timeouterr
from async_timeout import timeout
from . import exceptions

CONF_PERIOD = "period"

CONF_INSTANT = "instant_readings"
CONF_AMOUNT = "amount"
CONF_BUDGET = "budget"
CONF_COST = "cost"
CONF_CURRENT_VALUES = "current_values"

_RESOURCE = "https://engage.efergy.com/mobile_proxy/"

TIMEOUT = 10

_LOGGER = logging.getLogger(__name__)


class Efergy:
    """Implementation of Efergy object."""

    def __init__(
        self, api_token: str, loop: Any, session: ClientSession, utc_offset: str = "0"
    ) -> None:
        """Initialize."""
        self._api_token = api_token
        self._utc_offset = utc_offset
        self._loop = loop
        self._session = session

    async def get_sids(self) -> str:
        """Get current values sids."""
        url = f"{_RESOURCE}getCurrentValuesSummary?token={self._api_token}"
        return await self._async_send_get(url, CONF_CURRENT_VALUES)

    async def async_get_reading(
        self,
        reading_type: str,
        api_token: str | None = None,
        utc_offset: str | None = None,
        period: str = "year",
        sid: str = None,
        url: str = None,
        type_str: str = None,
    ) -> str:
        """Get specified reading type.

        'reading_type' is used to support Home Assistant sensor types.
        If this libary is used for other purposes, 'type_str' may be used.
        """
        self._api_token = api_token or self._api_token
        self._utc_offset = utc_offset or self._utc_offset
        if not type_str:
            if reading_type == CONF_INSTANT:
                url = f"{_RESOURCE}getInstant?token={self._api_token}"
                type_str = "reading"
            elif reading_type == CONF_AMOUNT:
                url = f"{_RESOURCE}getEnergy?token={self._api_token}&offset={self._utc_offset}&period={period}"
                type_str = "sum"
            elif reading_type == CONF_BUDGET:
                url = f"{_RESOURCE}getBudget?token={self._api_token}"
                type_str = "status"
            elif reading_type == CONF_COST:
                url = f"{_RESOURCE}getCost?token={self._api_token}&offset={self._utc_offset}&period={period}"
                type_str = "sum"
            elif reading_type == CONF_CURRENT_VALUES:
                url = f"{_RESOURCE}getCurrentValuesSummary?token={self._api_token}"
        _data = await self._async_send_get(url, type_str, sid=sid)

        if type_str:
            return _data[type_str]
        for sensor in _data:
            if sid == sensor["sid"]:
                return next(iter(sensor["data"][0].values()))

    async def _async_send_get(self, url: str, type_str: str, sid: str = None) -> str:
        """Send get request."""
        try:
            async with timeout(TIMEOUT, loop=self._loop):
                _response = await self._session.get(url)
                _data = await _response.json(content_type="text/html")
                if "description" in _data and _data["description"] == "bad token":
                    raise exceptions.InvalidAuth()
                return _data
        except timeouterr as ex:
            raise exceptions.ConnectTimeout() from ex
        except (ValueError, KeyError) as ex:
            _LOGGER.warning("Could not update status for efergy")
            raise exceptions.DataError() from ex
