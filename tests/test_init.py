"""Tests for PyEfergy object models."""

# pylint:disable=protected-access, too-many-lines, line-too-long
from aiohttp.client import ClientSession
import pytest

import pyefergy
from pyefergy import Efergy

from .conftest import API_KEY


@pytest.mark.asyncio
async def test_loop() -> None:
    """Test loop usage is handled correctly."""
    async with Efergy(API_KEY, utc_offset="America/New_York", currency="USD") as client:
        assert isinstance(client, Efergy)


@pytest.mark.asyncio
@pytest.mark.freeze_time("2022-01-03 00:00:00+00:00")
async def test_init(connection: None) -> None:
    """Test init."""
    client = Efergy(API_KEY, utc_offset="America/New_York", currency="USD")

    assert client._utc_offset == 300
    assert client.info["currency"] == "USD"

    async with ClientSession() as session:
        _client = Efergy(API_KEY, session=session, utc_offset="120")
        await _client.async_get_sids()

    assert _client._utc_offset == "120"

    with pytest.raises(pyefergy.exceptions.InvalidOffset):
        Efergy(API_KEY, utc_offset="abc")

    with pytest.raises(pyefergy.exceptions.InvalidCurrency):
        Efergy(API_KEY, utc_offset="America/New_York", currency="US")

    with pytest.raises(pyefergy.exceptions.InvalidPeriod):
        await client.async_get_sids()

    with pytest.raises(pyefergy.exceptions.DataError):
        await client.async_get_sids()

    with pytest.raises(pyefergy.exceptions.APICallLimit):
        await client.async_get_sids()

    with pytest.raises(pyefergy.exceptions.ServiceError):
        await client.async_get_sids()

    with pytest.raises(pyefergy.exceptions.InvalidAuth):
        await client.async_get_sids()

    with pytest.raises(pyefergy.exceptions.ServiceError):
        await client.async_get_reading("instant_readings")

    await client.async_get_sids()
    assert client.sids == [728386, 0, 728387]

    assert await client.async_get_reading("instant_readings") == 1580

    assert await client.async_get_reading("energy", period="day") == "38.21"

    assert await client.async_get_reading("cost", period="day") == "5.27"

    assert await client.async_get_reading("budget") == "ok"

    data = await client.async_get_reading("current_values")

    assert data["0"] == 1808
    assert data["728386"] == 218
    assert data["728387"] == 312

    assert await client.async_get_reading("current_values", sid=0) == 1808

    assert await client.async_hid_simple_tarrif(0.05) == {}

    data = await client.async_carbon(period="day", fromtime=0, totime=1)

    assert data["sum"] == "47.84"

    data = await client.async_channel_aggregated(
        fromtime=0,
        totime=1,
        aggperiod="week",
        type_str="none",
        aggfunc="sum",
        cachekey=3,
    )

    assert data["status"] == "ok"

    data = await client.async_comp_combined()
    assert data["day"]["avg"]["sum"] == 0

    data = await client.async_comp_day()
    assert data["day"]["avg"]["sum"] == 0

    data = await client.async_comp_week()
    assert data["week"]["avg"]["sum"] == 0

    data = await client.async_comp_month()
    assert data["month"]["avg"]["sum"] == 0

    data = await client.async_comp_year()
    assert data["year"]["avg"]["sum"] == 0

    data = await client.async_consumption_co2_graph(
        fromtime=1637884800, totime=1638489600000, aggperiod="week", cachekey=3
    )
    assert data["status"] == "ok"

    data = await client.async_generated_consumption_import(
        fromtime=1637884800, totime=1638489600, cachekey=3
    )
    assert data == {"consumption": 0, "generated": 0, "imported": 0}

    data = await client.async_generated_consumption_export(
        fromtime=1637884800, totime=1638489600, cachekey=3
    )
    assert data == {
        "consumedInHome": 0,
        "diverted": 0,
        "exported": 0,
        "generated": 0,
    }

    data = await client.async_country_list()
    assert data["UNITED KINGDOM"] == "230"
    assert await client.async_day() == {"1638552960000": [0.3, 0.33]}
    assert await client.async_week() == {"1638032400000": [0.29, 0.29]}
    assert await client.async_month() == {"1636156800000": [10.29, 13.81]}
    assert await client.async_year() == {"1606780800000": [421.41]}

    data = await client.async_estimated_combined()
    assert data["day_kwh"] == {"estimate": 11.73}

    data = await client.async_first_data()
    assert data["status"] == "ok"

    data = await client.async_forecast(period="day")
    assert data["day_kwh"] == {"estimate": 11.75}

    data = await client.async_generated_energy_revenue_carbon(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )
    assert data["status"] == "ok"

    data = await client.async_generated_consumption_graph(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )
    assert data["status"] == "ok"

    data = await client.async_generated_consumption_graph_costrev(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )
    assert data["status"] == "ok"

    data = await client.async_historical_values(period="week")
    assert data["status"] == "ok"

    data = await client.async_household()
    assert data["ageOfProperty"] == "5"

    data = await client.async_household_data_reference()
    assert data["profileoptions"]["ageOfProperty"]["values"][0]["key"] == "Pre 1851"

    data = await client.async_mac()
    assert data["listOfMacs"][0]["mac"] == "0004A3111111"

    data = await client.async_mac_status("0004A3905474")
    assert data["listOfMacs"][0]["mac"] == "0004A3111111"

    data = await client.async_pulse(1)
    assert data["status"] == "ok"
    assert data["pulses"] == 1000

    await client.async_status(get_sids=True)
    assert client.info["hid"] == "1234567890abcdef1234567890abcdef"
    assert client.info["mac"] == "ffffffffffff"
    assert client.info["status"] == "on"
    assert client.info["type"] == "EEEHub"
    assert client.info["version"] == "2.3.7"

    data = await client.async_tariff()
    assert data[0]["channel"] == "PWER"

    data = await client.async_time_series(
        1637884800,
        1638489600,
        aggperiod="week",
        aggfunc="sum",
        cache=True,
        datatype="cost",
    )
    assert data == {"data": {"1637884800000": ["undef"]}, "status": "ok"}

    data = await client.async_weather("Beijing", "China", timestamp=1637884800)
    assert data["temp_F"] == "70"

    data = await client.async_set_budget(100)
    assert data == {"monthly_budget": 250.0, "status": "ok"}

    with pytest.raises(pyefergy.exceptions.ConnectError):
        await client.async_get_reading("current_values")

    await client._session.close()
