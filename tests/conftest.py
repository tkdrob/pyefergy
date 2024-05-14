"""Tests configuration."""

# pylint:disable=redefined-outer-name
import asyncio
from asyncio import AbstractEventLoop
import json
import pathlib

from aresponses.main import ResponsesMockServer as Server
import pytest

from pyefergy import Efergy

API_KEY = "ur1234567-0abc12de3f456gh7ij89k012"
HOST = "engage.efergy.com"


def load_fixture(filename) -> str:
    """Load a fixture."""
    return pathlib.Path(__file__).parent.joinpath("fixtures", filename).read_text()


@pytest.fixture(autouse=True)
def loop_factory() -> AbstractEventLoop:
    """Create loop."""
    return asyncio.new_event_loop


@pytest.fixture(name="connection")
def _connection(aresponses: Server) -> None:
    """Add mocked connection."""
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=120",
        "GET",
        aresponses.Response(
            status=408,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=400,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error400.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error400_2.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error404.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error500.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("error403.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getInstant?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=json.dumps({"status": "error", "desc": "Method call failed"}),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getInstant?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("instant.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getEnergy?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("daily_energy.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCost?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("daily_cost.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getBudget?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("budget.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/createHidSimpleTariff?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cost_per_kwh=0.05",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCarbon?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day&fromTime=0&toTime=1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("carbon.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getChannelAggregated?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=0&toTime=1&aggPeriod=week&cacheTTL=60&type=none&aggFunc=sum&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("channelaggregated.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCompCombined?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compcombined.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCompDay?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compday.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCompWeek?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compweek.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCompMonth?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compmonth.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCompYear?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("compyear.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getConsumptionCostCO2Graph?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&aggPeriod=week&cacheTTL=60&cacheKey=3&fromTime=1637884800&toTime=1638489600000",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("consumptioncostco2graph.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getConsumptionGeneratedAndImport?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cacheTTL=60&cacheKey=3&fromTime=1637884800&toTime=1638489600",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_import.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getGeneratedConsumptionAndExport?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_export.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getCountryList?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("countrylist.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getDay?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("day.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getWeek?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("week.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getMonth?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&getPreviousPeriod=0&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("month.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getYear?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&cache=True&dataType=kwh",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("year.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getEstCombined?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("estimatedcombined.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getFirstData?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("firstdata.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getForecast?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=day",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("consumptionforecast.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getGeneratedEnergyRevenueCarbon?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3&aggPeriod=week",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generatedenergyrevenuecarbon.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getGenerationConsumptionGraph?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3&aggPeriod=week",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generatedconsumptiongraph.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getGenerationConsumptionGraphCostRevenue?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&aggPeriod=week&fromTime=1637884800&toTime=1638489600&cacheTTL=60&cacheKey=3",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("generated_consumption_graph_costrev.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getHV?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&period=week&type=PWER",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("historical_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getHousehold?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("household.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getHouseholdDataReference?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("household_data_reference.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getMAC?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("mac.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getMACStatus?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&mac_address=0004A3905474",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("mac_status.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getPulse?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&sid=1",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("pulse.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
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
        HOST,
        "/mobile_proxy/getCurrentValuesSummary?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("current_values.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getTariff?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("tariff.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getTimeSeries?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&fromTime=1637884800&toTime=1638489600&aggPeriod=week&aggFunc=sum&cache=True&dataType=cost",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("time_series.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/getWeather?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&city=Beijing&country=China&timestamp=1637884800",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("weather.json"),
        ),
        match_querystring=True,
    )
    aresponses.add(
        HOST,
        "/mobile_proxy/setBudget?token=ur1234567-0abc12de3f456gh7ij89k012&offset=300&budget=100",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "text/html"},
            text=load_fixture("budget.json"),
        ),
        match_querystring=True,
    )


@pytest.fixture()
def client():
    """Create Client."""
    return Efergy(API_KEY, utc_offset="America/New_York", currency="USD")
