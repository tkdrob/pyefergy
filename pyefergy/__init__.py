"""An API library for Efergy energy meters."""
from __future__ import annotations

from asyncio.exceptions import TimeoutError as timeouterr
from datetime import datetime
import logging
from typing import Any
import iso4217

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientConnectorError
from pytz import all_timezones, timezone as tz

from . import exceptions

CACHETTL = "cachettl"
COST = "cost"
CURRENCY = "currency"
DATA = "data"
DEFAULT_PERIOD = "month"
DEFAULT_TYPE = "kwh"
DESC = "description"
ERROR = "error"
HID = "hid"
ID = "id"
INSTANT = "instant_readings"
LISTOFMACS = "listOfMacs"
MAC = "mac"
MORE = "more"
SID = "sid"
STATUS = "status"
SUM = "sum"
TYPE = "type"
UTC_OFFSET = "utc_offset"
VERSION = "version"

_ALTERNATE_RES = "https://www.energyhive.com/mobile_proxy/"
_RES = "https://engage.efergy.com/mobile_proxy/"

_LOGGER = logging.getLogger(__name__)

TIMEOUT = 10


class Efergy:
    """Implementation of Efergy object."""

    def __init__(
        self,
        api_key: str,
        session: ClientSession = None,
        **kwargs: Any,
    ) -> None:
        """Initialize.

        utc_offset may be a string of 4 digits to represent the offset from UTC
        (ex. 0400) HH:MM or a TZ database name:
        https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

        Set alt to true to use the alternate API endpoint.
        """
        self._session = ClientSession() if session is None else session
        self.info = {}
        self._utc_offset = 0
        self._cachettl = 60
        self.update_params(api_key=api_key, **kwargs)

    def update_params(
        self,
        api_key: str = None,
        **kwargs: Any,
    ) -> None:
        """Update API key and UTC offset.

        kwargs can include:
        cachettl: int, alt: bool, utc_offset, and currency: ISO 4217 code.
        """
        self._api_key = api_key if api_key else self._api_key
        if CACHETTL in kwargs:
            self._cachettl = kwargs[CACHETTL]
        self._res = _ALTERNATE_RES if "alt" in kwargs else _RES
        if CURRENCY in kwargs:
            for cty in list(iso4217.raw_table.values()):
                if kwargs[CURRENCY] == cty["Ccy"]:
                    self.info[CURRENCY] = kwargs[CURRENCY]
                    break
            if CURRENCY not in self.info:
                raise exceptions.InvalidCurrency("Provided currency is invalid")
        if UTC_OFFSET in kwargs:
            utc_offset = str(kwargs[UTC_OFFSET])
            if utc_offset in all_timezones:
                utc_offset = int(datetime.now(tz(utc_offset)).strftime("%z"))
                self._utc_offset = -(int(utc_offset/100*60))
            elif utc_offset.isnumeric():
                self._utc_offset = utc_offset
            else:
                raise exceptions.InvalidOffset("Provided offset is invalid")

    async def _async_req(self, url: str) -> str | list:
        """Send get request."""
        _data = None
        try:
            _response = await self._session.get(
                url=url,
                timeout=ClientTimeout(TIMEOUT),
            )
            _data = await _response.json(content_type="text/html")
        except (timeouterr, ClientConnectorError) as ex:
            raise exceptions.ConnectError() from ex
        except (ValueError, KeyError) as ex:
            raise exceptions.DataError(_data) from ex
        if DESC in _data and _data[DESC] == "bad token":
            raise exceptions.InvalidAuth("Provided API token is invalid.")
        if ERROR in _data and _data[ERROR][ID] == 400:
            if "period" in _data[ERROR][MORE]:
                raise exceptions.InvalidPeriod(
                    "Provided period is invalid. Options are: day, week, month, year"
                )
            raise exceptions.DataError(_data)
        if ERROR in _data and _data[ERROR][ID] == 404:
            raise exceptions.APICallLimit(
                "API key has reached calls per day allowed limit"
            )
        if ERROR in _data and _data[ERROR][ID] == 500:
            raise exceptions.ServiceError(
                "Error communicating with sensor/hub. Check connections"
            )
        return _data

    async def async_get_sids(self) -> None:
        """Get current values sids."""
        url = f"{self._res}getCurrentValuesSummary?token={self._api_key}"
        sids = []
        for sid in await self._async_req(url):
            sids.append(sid[SID])
        self.info["sids"] = sids

    async def async_get_reading(
        self,
        reading_type: str,
        period: str = DEFAULT_PERIOD,
        sid: str = None,
    ) -> str | dict:
        """Get reading for instant, budget, or summary.

        'reading_type' can be any of the following:
        instant: Current Watt usage.
        energy: kWh of energy used during specified period.
        cost: Cost of energy used during specified period.
        budget: Currently set budget and status of that budget.
        current_values: Values for each sensor attached to the account.

        The API treats monthly data as 28 days as months vary in the number of days.
        'reading type' for energy and cost may include
        extra characters for easier keying by period.
        """
        type_str = None
        if reading_type == INSTANT:
            _url = f"{self._res}getInstant?token={self._api_key}"
            type_str = "reading"
        elif "energy" in reading_type:
            _url = f"{self._res}getEnergy?token={self._api_key}"
            _url = f"{_url}&offset={self._utc_offset}&period={period}"
            type_str = SUM
        elif COST in reading_type:
            _url = f"{self._res}getCost?token={self._api_key}"
            _url = f"{_url}&offset={self._utc_offset}&period={period}"
            type_str = SUM
        elif reading_type == "budget":
            _url = f"{self._res}getBudget?token={self._api_key}"
            type_str = STATUS
        elif reading_type == "current_values":
            _url = f"{self._res}getCurrentValuesSummary?token={self._api_key}"
        _data = await self._async_req(_url)
        if (
            CURRENCY in self.info
            and COST in reading_type
            and self.info[CURRENCY] != _data["units"]
        ):
            _LOGGER.debug(
                "Currency provided does not match device settings. "
                "This can affect energy cost statistics"
            )
        if type_str:
            return _data[type_str]
        _readings = {}
        for sensor in _data:
            if sid == sensor[SID]:
                return list(sensor[DATA][0].values())[0]
            _readings[sensor[SID]] = list(sensor[DATA][0].values())[0]
        return _readings

    async def async_hid_simple_tarrif(self, cost: str | int) -> dict:
        """Create and Apply tariff. Only requires a pence per kWh value."""
        _url = f"{self._res}createHidSimpleTariff?token={self._api_key}&cost_per_kwh={cost}"
        return await self._async_req(_url)

    async def async_carbon(
        self,
        period: str = DEFAULT_PERIOD,
        fromtime: str | int = None,
        totime: str | int = None,
    ) -> dict:
        """Get amount of carbon generated by the energy production to meet the usage.

        of the household over a given period.
        By default the usage so far "this month" is returned.
        """
        _url = f"{self._res}getCarbon?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&period={period}&fromTime={fromtime}&toTime={totime}"
        return await self._async_req(_url)

    async def async_channel_aggregated(
        self,
        fromtime: str | int = None,
        totime: str | int = None,
        aggperiod: str = DEFAULT_PERIOD,
        type_str: str = None,
        aggfunc: str = SUM,
        cachekey: str = None,
    ) -> dict:
        """Return timeseries of aggregated devices on a given channel for an hid."""
        _url = f"{self._res}getChannelAggregated?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&fromTime={fromtime}&toTime={totime}"
        _url = f"{_url}&aggPeriod{aggperiod}&cacheTTL={self._cachettl}&type={type_str}"
        _url = f"{_url}&aggFunc={aggfunc}&cacheKey={cachekey}"
        return await self._async_req(_url)

    async def async_comp_combined(self) -> dict:
        """Retrieve comparison data between a given household and all other households.

        for day, week and month. The comparisons are also available elsewhere separately
        (getCompDay etc.)
        """
        _url = f"{self._res}getCompCombined?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}"
        return await self._async_req(_url)

    async def async_comp_day(self) -> dict:
        """Retrieve comparison data between a given household.

        and all other households over the period of a day.
        """
        _url = f"{self._res}getCompDay?token={self._api_key}&offset={self._utc_offset}"
        return await self._async_req(_url)

    async def async_comp_month(self) -> dict:
        """Retrieve comparison data between a given household.

        and all other households over the period of a month.
        """
        _url = f"{self._res}getCompMonth?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}"
        return await self._async_req(_url)

    async def async_comp_week(self) -> dict:
        """Retrieve comparison data between a given household.

        and all other households over the period of a week.
        """
        _url = f"{self._res}getCompWeek?token={self._api_key}&offset={self._utc_offset}"
        return await self._async_req(_url)

    async def async_comp_year(self) -> dict:
        """Retrieve comparison data between a given household.

        and all other households over the period of a year.
        """
        _url = f"{self._res}getCompYear?token={self._api_key}&offset={self._utc_offset}"
        return await self._async_req(_url)

    async def async_consumption_co2_graph(
        self,
        fromtime: str | int,
        totime: str | int,
        aggperiod: str = DEFAULT_PERIOD,
        cachekey: str = None,
    ) -> dict:
        """Return timeseries of consumed/cost and CO2."""
        _url = f"{self._res}getConsumptionCostCO2Graph?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&aggPeriod={aggperiod}"
        _url = f"{_url}&cacheTTL={self._cachettl}&cacheKey={cachekey or aggperiod}"
        _url = f"{_url}&fromTime={fromtime}&toTime={totime}"
        _data = await self._async_req(_url)
        return _data

    async def async_generated_consumption_import(
        self,
        fromtime: str | int,
        totime: str | int,
        cachekey: str = None,
    ) -> dict:
        """Deliver proportion of consumed power that is generated in the home.

        vs that imported. Only useful if PWER and PWER_GAC channels are present.
        """
        _url = f"{self._res}getConsumptionGeneratedAndImport?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&cacheTTL={self._cachettl}"
        _url = f"{_url}&cacheKey={cachekey}&fromTime={fromtime}&toTime={totime}"
        _data = await self._async_req(_url)
        return _data

    async def async_country_list(self) -> dict:
        """Retrieve list of countries with their associated voltage."""
        return await self._async_req(f"{self._res}getCountryList?token={self._api_key}")

    async def async_day(
        self, getpreviousperiod: int = None, cache: bool = True
    ) -> dict:
        """Retrieve historical timeseries of consumption data.

        for household for previous 24 hours.
        Data will be returned at a minute level of resolution.
        """
        _url = f"{self._res}getDay?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&getPreviousPeriod={getpreviousperiod}&cache={cache}"
        _data = await self._async_req(_url)
        return _data[DATA]

    async def async_estimated_combined(self) -> dict:
        """Retrieve estimated usage data for a given household for the current.

        day and current month.
        The comparisons are also available elsewhere separately (see getForecast)
        """
        _url = f"{self._res}getEstCombined?token={self._api_key}"
        return await self._async_req(_url)

    async def async_first_data(self) -> dict:
        """Return first data point time. (UTC)."""
        _data = await self._async_req(f"{self._res}getFirstData?token={self._api_key}")
        return _data

    async def async_forecast(self, period: str) -> dict:
        """Get forecast for energy consumption, greenhouse gas generation.

        or cost (if tariff set).
        """
        _url = f"{self._res}getForecast?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&period={period}"
        return await self._async_req(_url)

    async def async_generated_consumption_export(
        self,
        fromtime: str | int,
        totime: str | int,
        cachekey: str = None,
    ) -> dict:
        """Deliver proportion of generated power.

        that is used in the home vs that exported.
        Only useful if PWER and PWER_GAC channels are present.
        """
        _url = f"{self._res}getGeneratedConsumptionAndExport?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&fromTime={fromtime}&toTime="
        _url = f"{_url}{totime}&cacheTTL={self._cachettl}&cacheKey={cachekey}"
        return await self._async_req(_url)

    async def async_generated_energy_revenue_carbon(
        self,
        fromtime: str | int,
        totime: str | int,
        cachekey: str = None,
    ) -> dict:
        """Return a timeseries of consumed, revenue and c02 saved."""
        _url = f"{self._res}getGeneratedEnergyRevenueCarbon?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&fromTime={fromtime}&toTime="
        _url = f"{_url}{totime}&cacheTTL={self._cachettl}&cacheKey={cachekey}"
        return await self._async_req(_url)

    async def async_generated_consumption_graph(
        self,
        fromtime: str | int,
        totime: str | int,
        cachekey: str = None,
        aggperiod: str = DEFAULT_PERIOD,
    ) -> dict:
        """Deliver timeseries array of consumed/generated/genconsumed/exported/imported.

        Only useful if PWER and PWER_GAC channels are present.
        """
        _url = f"{self._res}getGenerationConsumptionGraph?token={self._api_key}"
        _url = f"{_url}&offset={self._utc_offset}&fromTime={fromtime}&toTime="
        _url = f"{_url}{totime}&cacheTTL={self._cachettl}&cacheKey={cachekey}"
        _url = f"{_url}&aggPeriod={aggperiod}"
        return await self._async_req(_url)

    async def async_generated_consumption_graph_costrev(
        self,
        fromtime: str | int,
        totime: str | int,
        cachekey: str = None,
        aggperiod: str = DEFAULT_PERIOD,
    ) -> dict:
        """Deliver timeseries array of consumed/generated/genconsumed/exported/imported.

        costs/revenue.
        Only useful if PWER and PWER_GAC channels are present.
        """
        _url = f"{self._res}getGenerationConsumptionGraphCostRevenue?token="
        _url = f"{_url}{self._api_key}&aggPeriod={aggperiod}"
        _url = f"{_url}&offset={self._utc_offset}&fromTime={fromtime}&toTime="
        _url = f"{_url}{totime}&cacheTTL={self._cachettl}&cacheKey={cachekey}"
        return await self._async_req(_url)

    async def async_historical_values(
        self, period: str = DEFAULT_PERIOD, type_str: str = "PWER"
    ) -> dict:
        """Return array of historical values."""
        _url = f"{self._res}getHV?token={self._api_key}&period={period}&type{type_str}"
        return await self._async_req(_url)

    async def async_household(self) -> dict:
        """Get household attributes as set in setHousehold.php."""
        return await self._async_req(f"{self._res}getHousehold?token={self._api_key}")

    async def async_household_data_reference(self) -> dict:
        """Return a set of allowed values for setting the household attributes."""
        _url = f"{self._res}getHouseholdDataReference?token={self._api_key}"
        return await self._async_req(_url)

    async def async_mac(self) -> dict:
        """Set the list of MACs as a listOfMACs for a valid householder ID (HID)."""
        return await self._async_req(f"{self._res}getMAC?token={self._api_key}")

    async def async_mac_status(self, mac: str) -> dict:
        """Retrieve the device status for a given MAC."""
        _url = f"{self._res}getMACStatus?token={self._api_key}&mac_address={mac}"
        return await self._async_req(_url)

    async def async_month(
        self,
        getpreviousperiod: int = None,
        cache: bool = True,
        datatype: str = DEFAULT_TYPE,
    ) -> dict:
        """Retrieve the historical timeseries of consumption data.

        or a household for the previous month.
        Data will be returned at a day level of resolution.
        """
        _url = f"{self._res}getMonth?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&getPreviousPeriod={getpreviousperiod}&cache={cache}"
        _url = f"{_url}&dataType={datatype}"
        _data = await self._async_req(_url)
        return _data[DATA]

    async def async_pulse(self, sid: str | int) -> dict:
        """Get the pulse rate for a given IR clamp."""
        _url = f"{self._res}getPulse?token={self._api_key}&sid={sid}"
        return await self._async_req(_url)

    async def async_status(self, get_sids: bool = False) -> dict:
        """Retrieve the device status as a list of statuses."""
        _data = await self._async_req(f"{self._res}getStatus?token={self._api_key}")
        self.info[HID] = _data[HID]
        self.info[MAC] = _data[LISTOFMACS][0][MAC]
        self.info[STATUS] = _data[LISTOFMACS][0][STATUS]
        self.info[TYPE] = None
        if TYPE in _data[LISTOFMACS][0]:
            self.info[TYPE] = _data[LISTOFMACS][0][TYPE]
        self.info[VERSION] = _data[LISTOFMACS][0][VERSION]
        if get_sids:
            await self.async_get_sids()
        return _data

    async def async_tarrif(self) -> dict:
        """Return the tariff structure(s) for the HID supplied.

        (limited by optional sid).
        """
        _data = await self._async_req(f"{self._res}getTariff?token={self._api_key}")
        return _data[DATA]

    async def async_time_series(
        self,
        fromtime: str | int,
        totime: str | int,
        aggperiod: str = DEFAULT_PERIOD,
        aggfunc: str = SUM,
        cache: bool = True,
        datatype: str = DEFAULT_TYPE,
    ) -> dict:
        """Retrieve the historical timeseries of consumption data.

        for a household over the specified period.
        `fromtime` and `totime` are expressed in epoch timestamp
        data_type: cost or kwh
        """
        _url = f"{self._res}getTimeSeries?token={self._api_key}&offset="
        _url = f"{_url}{self._utc_offset}&fromTime={fromtime}&toTime={totime}"
        _url = f"{_url}&appPeriod={aggperiod}&aggFunc={aggfunc}&cache="
        _url = f"{_url}{cache}&dataType={datatype}"
        _data = await self._async_req(_url)
        return _data[DATA]

    async def async_weather(
        self, city: str, country: str, timestamp: str = None
    ) -> dict:
        """Get the current weather for the location of the HID."""
        _url = f"{self._res}getWeather?token={self._api_key}&city={city}&country="
        _url = f"{_url}{country}&timestamp={timestamp}"
        return await self._async_req(_url)

    async def async_week(
        self,
        getpreviousperiod: int = None,
        cache: bool = True,
        datatype: str = DEFAULT_TYPE,
    ) -> dict:
        """Retrieve the historical timeseries of consumption data.

        for a household for the previous week.
        Data will be returned at a hour level of resolution.
        """
        _url = f"{self._res}getWeek?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&getPreviousPeriod={getpreviousperiod}&cache={cache}"
        _url = f"{_url}&dataType={datatype}"
        _data = await self._async_req(_url)
        return _data[DATA]

    async def async_year(
        self,
        cache: bool = True,
        datatype: str = DEFAULT_TYPE,
    ) -> dict:
        """Retrieve the historical timeseries of consumption data.

        for a household for the previous year.
        Data will be returned at a month level of resolution.
        """
        _url = f"{self._res}getYear?token={self._api_key}&offset={self._utc_offset}"
        _url = f"{_url}&cache={cache}&dataType={datatype}"
        _data = await self._async_req(_url)
        return _data[DATA]

    async def async_set_budget(self, budget: float) -> str:
        """Set a value for the monthly budget for a HID."""
        _url = f"{self._res}setBudget?token={self._api_key}&budget={budget}"
        _data = await self._async_req(_url)
        return _data[STATUS]
