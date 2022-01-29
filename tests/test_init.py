"""Tests for PyEfergy object models."""
# pylint:disable=protected-access, too-many-lines, line-too-long
import asyncio
import json

from aiohttp.client import ClientSession
import pytest

import pyefergy
from pyefergy import Efergy

from . import API_KEY, load_fixture


@pytest.mark.asyncio
async def test_loop() -> None:
    """Test loop usage is handled correctly."""
    async with Efergy(API_KEY, utc_offset="America/New_York", currency="USD") as client:
        assert isinstance(client, Efergy)


@pytest.mark.asyncio
async def test_init(aresponses, client: Efergy) -> None:
    """Test init."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=120",
        "GET",
        aresponses.Response(
            status=408,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
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


@pytest.mark.asyncio
async def test_error_400(aresponses, client: Efergy) -> None:
    """Test error 400."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=400,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error400.json"),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.InvalidPeriod):
        await client.async_get_sids()


@pytest.mark.asyncio
async def test_error_400_2(aresponses, client: Efergy) -> None:
    """Test error 400."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error400_2.json"),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.DataError):
        await client.async_get_sids()


@pytest.mark.asyncio
async def test_error_404(aresponses, client: Efergy) -> None:
    """Test error 404."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error404.json"),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.APICallLimit):
        await client.async_get_sids()


@pytest.mark.asyncio
async def test_error_500(aresponses, client: Efergy) -> None:
    """Test error 500."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error500.json"),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.ServiceError):
        await client.async_get_sids()


@pytest.mark.asyncio
async def test_error_403(aresponses, client: Efergy) -> None:
    """Test error 403."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error403.json"),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.InvalidAuth):
        await client.async_get_sids()


@pytest.mark.asyncio
async def test_timeout(aresponses, client: Efergy) -> None:
    """Test timeout."""

    async def response_handler():
        await asyncio.sleep(0)
        return aresponses.Response(body="Timeout!")

    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=0",
        "GET",
        await response_handler(),
    )

    with pytest.raises(pyefergy.exceptions.ConnectError):
        await client.async_get_reading("current_values")


@pytest.mark.asyncio
async def test_method_call_failed(aresponses, client: Efergy) -> None:
    """Test method call failed."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getInstant?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=json.dumps({"status": "error", "desc": "Method call failed"}),
        ),
        match_querystring=True,
    )

    with pytest.raises(pyefergy.exceptions.ServiceError):
        await client.async_get_reading("instant_readings")


@pytest.mark.asyncio
async def test_async_get_sids(aresponses, client: Efergy) -> None:
    """Test getting sids."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )

    await client.async_get_sids()
    assert client.sids == [728386, 0, 728387]


@pytest.mark.asyncio
async def test_async_get_instant(aresponses, client: Efergy) -> None:
    """Test getting instant reading."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getInstant?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("instant.json"),
        ),
        match_querystring=True,
    )
    assert await client.async_get_reading("instant_readings") == 1580


@pytest.mark.asyncio
async def test_async_get_energy(aresponses, client: Efergy) -> None:
    """Test getting energy reading."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getEnergy?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("daily_energy.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_get_reading("energy", period="day") == "38.21"


@pytest.mark.asyncio
async def test_async_get_cost(aresponses, client: Efergy) -> None:
    """Test getting cost reading."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCost?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("daily_cost.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_get_reading("cost", period="day") == "5.27"


@pytest.mark.asyncio
async def test_async_get_budget(aresponses, client: Efergy) -> None:
    """Test getting budget."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getBudget?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("budget.json"),
        ),
        match_querystring=True,
    )
    assert await client.async_get_reading("budget") == "ok"


@pytest.mark.asyncio
async def test_async_get_current_values(aresponses, client: Efergy) -> None:
    """Test getting current values."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_get_reading("current_values")

    assert data["0"] == 1808
    assert data["728386"] == 218
    assert data["728387"] == 312

    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_get_reading("current_values", sid=0) == 1808


@pytest.mark.asyncio
async def test_async_hid_simple_tarrif(aresponses, client: Efergy) -> None:
    """Test creating hid simple tarrif."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/createHidSimpleTariff?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cost_per_kwh=0.05",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
        match_querystring=True,
    )

    assert await client.async_hid_simple_tarrif(0.05) == {}


@pytest.mark.asyncio
async def test_async_carbon(aresponses, client: Efergy) -> None:
    """Test getting carbon reading."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCarbon?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day&fromTime=0&toTime=1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("carbon.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_carbon(period="day", fromtime=0, totime=1)

    assert data["sum"] == "47.84"


@pytest.mark.asyncio
async def test_async_channel_aggregated(aresponses, client: Efergy) -> None:
    """Test getting aggregated channels."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getChannelAggregated?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=0&toTime=1&aggPeriod=week&cacheTTL=60&type=none&aggFunc=sum&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("channelaggregated.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_channel_aggregated(
        fromtime=0,
        totime=1,
        aggperiod="week",
        type_str="none",
        aggfunc="sum",
        cachekey=3,
    )

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_comp_combined(aresponses, client: Efergy) -> None:
    """Test getting comparison data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCompCombined?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compcombined.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_comp_combined()

    assert data["day"]["avg"]["sum"] == 0


@pytest.mark.asyncio
async def test_async_comp_day(aresponses, client: Efergy) -> None:
    """Test getting comparison data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCompDay?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compday.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_comp_day()

    assert data["day"]["avg"]["sum"] == 0


@pytest.mark.asyncio
async def test_async_comp_week(aresponses, client: Efergy) -> None:
    """Test getting comparison data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCompWeek?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compweek.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_comp_week()

    assert data["week"]["avg"]["sum"] == 0


@pytest.mark.asyncio
async def test_async_comp_month(aresponses, client: Efergy) -> None:
    """Test getting comparison data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCompMonth?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compmonth.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_comp_month()

    assert data["month"]["avg"]["sum"] == 0


@pytest.mark.asyncio
async def test_async_comp_year(aresponses, client: Efergy) -> None:
    """Test getting comparison data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCompYear?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compyear.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_comp_year()

    assert data["year"]["avg"]["sum"] == 0


@pytest.mark.asyncio
async def test_async_consumption_co2_graph(aresponses, client: Efergy) -> None:
    """Test getting consumption co2 data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getConsumptionCostCO2Graph?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&aggPeriod=week&cacheTTL=60&cacheKey=3&fromTime=1637884800&toTime=1638489600000",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("consumptioncostco2graph.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_consumption_co2_graph(
        fromtime=1637884800, totime=1638489600000, aggperiod="week", cachekey=3
    )

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_consumption_import(aresponses, client: Efergy) -> None:
    """Test getting consumption import data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getConsumptionGeneratedAndImport?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cacheTTL=60&cacheKey=3&fromTime=1637884800&toTime=1638489600",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_import.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_generated_consumption_import(
        fromtime=1637884800, totime=1638489600, cachekey=3
    )

    assert data == {"consumption": 0, "generated": 0, "imported": 0}


@pytest.mark.asyncio
async def test_async_generated_consumption_export(aresponses, client: Efergy) -> None:
    """Test getting consumption export data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getGeneratedConsumptionAndExport?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_export.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_generated_consumption_export(
        fromtime=1637884800, totime=1638489600, cachekey=3
    )

    assert data == {
        "consumedInHome": 0,
        "diverted": 0,
        "exported": 0,
        "generated": 0,
    }


@pytest.mark.asyncio
async def test_async_country_list(aresponses, client: Efergy) -> None:
    """Test getting consumption co2 data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCountryList?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("countrylist.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_country_list()

    assert data["UNITED KINGDOM"] == "230"


@pytest.mark.asyncio
async def test_async_day(aresponses, client: Efergy) -> None:
    """Test getting day data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getDay?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("day.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_day() == {"1638552960000": [0.3, 0.33]}


@pytest.mark.asyncio
async def test_async_week(aresponses, client: Efergy) -> None:
    """Test getting week data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getWeek?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("week.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_week() == {"1638032400000": [0.29, 0.29]}


@pytest.mark.asyncio
async def test_async_month(aresponses, client: Efergy) -> None:
    """Test getting month data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getMonth?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("month.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_month() == {"1636156800000": [10.29, 13.81]}


@pytest.mark.asyncio
async def test_async_year(aresponses, client: Efergy) -> None:
    """Test getting year data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getYear?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("year.json"),
        ),
        match_querystring=True,
    )

    assert await client.async_year() == {"1606780800000": [421.41]}


@pytest.mark.asyncio
async def test_async_estimated_combined(aresponses, client: Efergy) -> None:
    """Test getting estimated combined usage data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getEstCombined?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("estimatedcombined.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_estimated_combined()

    assert data["day_kwh"] == {"estimate": 11.73}


@pytest.mark.asyncio
async def test_async_first_data(aresponses, client: Efergy) -> None:
    """Test getting first data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getFirstData?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("firstdata.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_first_data()

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_forecast(aresponses, client: Efergy) -> None:
    """Test getting consumption forecast data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getForecast?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("consumptionforecast.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_forecast(period="day")

    assert data["day_kwh"] == {"estimate": 11.75}


@pytest.mark.asyncio
async def test_async_generated_energy_revenue_carbon(
    aresponses, client: Efergy
) -> None:
    """Test getting generated energy revenue carbon data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getGeneratedEnergyRevenueCarbon?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3&aggPeriod=week",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generatedenergyrevenuecarbon.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_generated_energy_revenue_carbon(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_generated_consumption_graph(aresponses, client: Efergy) -> None:
    """Test getting generated consumption graph data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getGenerationConsumptionGraph?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3&aggPeriod=week",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generatedconsumptiongraph.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_generated_consumption_graph(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_generated_consumption_graph_costrev(
    aresponses, client: Efergy
) -> None:
    """Test getting generated consumption cost and revenue graph data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getGenerationConsumptionGraphCostRevenue?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&aggPeriod=week&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_graph_costrev.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_generated_consumption_graph_costrev(
        1637884800, 1638489600, aggperiod="week", cachekey=3
    )

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_historical_values(aresponses, client: Efergy) -> None:
    """Test getting historical data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getHV?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=week&type=PWER",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("historical_values.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_historical_values(period="week")

    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_async_household(aresponses, client: Efergy) -> None:
    """Test getting household data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getHousehold?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("household.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_household()

    assert data["ageOfProperty"] == "5"


@pytest.mark.asyncio
async def test_async_household_data_reference(aresponses, client: Efergy) -> None:
    """Test getting household data reference."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getHouseholdDataReference?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("household_data_reference.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_household_data_reference()

    assert data["profileoptions"]["ageOfProperty"]["values"][0]["key"] == "Pre 1851"


@pytest.mark.asyncio
async def test_async_mac(aresponses, client: Efergy) -> None:
    """Test getting mac addresses."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getMAC?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("mac.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_mac()

    assert data["listOfMacs"][0]["mac"] == "0004A3111111"


@pytest.mark.asyncio
async def test_async_mac_status(aresponses, client: Efergy) -> None:
    """Test getting mac address data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getMACStatus?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&mac_address=0004A3905474",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("mac_status.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_mac_status("0004A3905474")

    assert data["listOfMacs"][0]["mac"] == "0004A3111111"


@pytest.mark.asyncio
async def test_async_pulse(aresponses, client: Efergy) -> None:
    """Test getting sid pulse data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getPulse?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&sid=1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("pulse.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_pulse(1)

    assert data["status"] == "ok"
    assert data["pulses"] == 1000


@pytest.mark.asyncio
async def test_async_status(aresponses, client: Efergy) -> None:
    """Test getting device status."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getStatus?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("status.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )

    await client.async_status(get_sids=True)

    assert client.info["hid"] == "1234567890abcdef1234567890abcdef"
    assert client.info["mac"] == "ffffffffffff"
    assert client.info["status"] == "on"
    assert client.info["type"] == "EEEHub"
    assert client.info["version"] == "2.3.7"


@pytest.mark.asyncio
async def test_async_tariff(aresponses, client: Efergy) -> None:
    """Test getting tariff data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getTariff?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("tariff.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_tariff()

    assert data[0]["channel"] == "PWER"


@pytest.mark.asyncio
async def test_async_time_series(aresponses, client: Efergy) -> None:
    """Test getting historical timeseries data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getTimeSeries?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&aggPeriod=week&aggFunc=sum&cache=True&dataType=cost",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("time_series.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_time_series(
        1637884800,
        1638489600,
        aggperiod="week",
        aggfunc="sum",
        cache=True,
        datatype="cost",
    )

    assert data == {"data": {"1637884800000": ["undef"]}, "status": "ok"}


@pytest.mark.asyncio
async def test_async_weather(aresponses, client: Efergy) -> None:
    """Test getting weather data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/getWeather?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&city=Beijing&country=China&timestamp=1637884800",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("weather.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_weather("Beijing", "China", timestamp=1637884800)

    assert data["temp_F"] == "70"


@pytest.mark.asyncio
async def test_async_set_budget(aresponses, client: Efergy) -> None:
    """Test getting weather data."""
    aresponses.add(
        "engage.efergy.com",
        "/mobile_proxy/setBudget?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&budget=100",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("budget.json"),
        ),
        match_querystring=True,
    )

    data = await client.async_set_budget(100)

    assert data == {"monthly_budget": 250.0, "status": "ok"}
