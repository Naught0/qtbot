import json
import re
from collections.abc import Mapping, Sequence
from datetime import datetime
from io import BytesIO
from urllib.parse import quote

import discord
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from aiohttp import ClientSession
from dateutil.parser import parse as parse_date
from discord.ext import commands
from yarl import URL

from utils.custom_context import CustomContext


class MissingEntitlementToken(Exception): ...


async def get_entitlement_token(session: ClientSession) -> str:
    url = "https://www.marketwatch.com/"
    headers = {
        "accept-language": "en-US,en;q=0.9",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36",
    }

    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        html = await response.text()
        match = re.search(r'"entitlementToken":"([^"]+)"', html)

        if match:
            token = match.group(1)
            return token
        else:
            raise MissingEntitlementToken("Entitlement token not found in HTML")


async def get_quote_data(
    session: ClientSession, ticker: str, entitlement_token: str, ckey: str
) -> Mapping:
    api_url = "https://api.wsj.net/api/dylan/quotes/v2/comp/quoteByDialect"
    params = {
        "dialect": "charting",
        "needed": "CompositeTrading|BluegrassChannels",
        "MaxInstrumentMatches": 1,
        "accept": "application/json",
        "EntitlementToken": entitlement_token,
        "ckey": ckey,
        "dialects": "Charting",
        "id": ticker,
    }

    resp = await session.get(api_url, params=params)
    resp.raise_for_status()
    data = await resp.json()
    return data


async def fetch_wsj_data(
    session: ClientSession, ticker: str, entitlement_token: str
) -> Mapping:
    ckey = entitlement_token[:10]
    quote_data = await get_quote_data(session, ticker, entitlement_token, ckey)
    return quote_data["InstrumentResponses"][0]["Matches"][0]


async def fetch_historical_data(
    session: ClientSession, token: str, dialect: str
) -> tuple[list[datetime], list[list[int]]]:
    json_data = {
        "Step": "P1D",
        "TimeFrame": "P1Y",
        "EntitlementToken": token,
        "IncludeMockTick": True,
        "FilterNullSlots": False,
        "FilterClosedPoints": True,
        "IncludeClosedSlots": False,
        "IncludeOfficialClose": True,
        "InjectOpen": False,
        "ShowPreMarket": False,
        "ShowAfterHours": False,
        "UseExtendedTimeFrame": True,
        "WantPriorClose": True,
        "IncludeCurrentQuotes": False,
        "ResetTodaysAfterHoursPercentChange": False,
        "Series": [
            {
                "Key": dialect,
                "Dialect": "Charting",
                "Kind": "Ticker",
                "SeriesId": "s1",
                "DataTypes": ["Last"],
            }
        ],
    }
    params = {
        "ckey": token[:10],
    }
    resp = await session.get(
        URL(
            f"https://api.wsj.net/api/michelangelo/timeseries/history?json={quote(json.dumps(json_data, separators=(',',':')), safe='')}",
            encoded=True,
        ),
        params=params,
        headers={
            "accept-language": "en-US,en;q=0.9",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
            "Dylan2010.Entitlementtoken": token,
            "Accept": "application/json, text/javascript, */*; q=0.01",
        },
    )
    resp.raise_for_status()
    data = await resp.json()

    return [datetime.fromtimestamp(x / 1000) for x in data["TimeInfo"]["Ticks"]], data[
        "Series"
    ][0]["DataPoints"]


def create_graph(xdata: Sequence, ydata: Sequence[Sequence[int]]) -> BytesIO:
    plt.style.use("dark_background")
    plt.rcParams["figure.figsize"] = (4, 2.3)
    fig, ax = plt.subplots()

    ax.plot(xdata, ydata, color="khaki", linewidth=1)
    ax.set_ylabel("Price (USD)", fontsize=12, color="lightgrey")
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.tick_params(colors="lightgrey")
    for spine in ax.spines.values():
        spine.set_edgecolor("grey")
    ax.grid(True, alpha=0.4, color="lightgrey")
    fig.autofmt_xdate()

    file = BytesIO()
    plt.savefig(file, format="webp", bbox_inches="tight")

    return file


class Stonks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="stonk", aliases=["stock", "stocks", "stonks"])
    async def stonk(self, ctx: CustomContext, *, symbol: str):
        """Get current information on a stonk"""
        async with ClientSession() as session:
            entitlement_token = await get_entitlement_token(session)
            resp = await fetch_wsj_data(session, symbol, entitlement_token)
            dialect_symbols = resp["DialectSymbols"][0]["Symbols"][0]
            x, y = await fetch_historical_data(
                session, entitlement_token, dialect_symbols
            )

        if not resp:
            return await ctx.error("Couldn't find a matching stock")

        graph = create_graph(x, y)
        graph.seek(0)
        graph_file_name = f"{symbol}-{datetime.now().timestamp():.0f}.webp"
        file = discord.File(graph, filename=graph_file_name)

        ticker = resp["Instrument"]["Ticker"]
        name = resp["Instrument"]["CommonName"]
        price_data = resp["CompositeTrading"]
        last_price = price_data["Last"]["Price"]["Value"]
        currency = price_data["Last"]["Price"]["Iso"]
        open_ = price_data["Open"]["Value"]
        high = price_data["High"]["Value"]
        low = price_data["Low"]["Value"]
        percent_change = price_data["NetChange"]["Value"]

        em = discord.Embed(
            title=f"{name} - {ticker}",
            color=(
                discord.Color.dark_green()
                if percent_change > 0
                else discord.Color.dark_red()
            ),
        )
        em.url = f"https://finance.yahoo.com/quote/{ticker}"
        em.add_field(
            name=f"Last Price in {currency}",
            value=f"${last_price:,.2f}",
        )
        em.add_field(
            name="Percent Change",
            value=f"{percent_change:,.2f}%",
            inline=False,
        )
        em.add_field(name="Open", value=f"${open_:,.2f}")
        em.add_field(name="High", value=f"${high:,.2f}")
        em.add_field(name="Low", value=f"${low:,.2f}")
        em.set_footer(text="last updated")
        em.timestamp = parse_date(price_data["Last"]["Time"])
        em.set_image(url=f"attachment://{graph_file_name}")

        await ctx.send(embed=em, file=file)


async def setup(bot):
    await bot.add_cog(Stonks(bot))
