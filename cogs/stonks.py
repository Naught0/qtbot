from __future__ import annotations

import os
import pickle
from datetime import datetime, timedelta
from io import BytesIO
from traceback import print_exc
from typing import TypedDict

import aiohttp
import discord
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
from aiohttp import ClientSession
from discord.ext import commands
from redis.asyncio import Redis

from utils.cache import redis_client
from utils.custom_context import CustomContext


class MassiveClient:
    _base_url = "https://api.massive.com"

    def __init__(
        self,
        api_key: str,
        redis: Redis | None = None,
        session: ClientSession | None = None,
    ):
        self._api_key = api_key
        if redis is None:
            self._redis = redis_client
        else:
            self._redis = redis

        if session is None:
            self._session = ClientSession()
            self._owns_session = True
        else:
            self._owns_session = False
            self._session = session

    async def _get(self, endpoint: str, params={}, **kwargs):
        return await self._session.get(
            f"{self._base_url}{endpoint}",
            params={**params, "apiKey": self._api_key},
            **kwargs,
        )

    async def _set_cache(self, key: str, data, ex: int | None = 60 * 60):
        print("Cache miss:", key)
        await self._redis.set(key, pickle.dumps(data), ex=ex)

    async def _get_cache(self, key: str):
        try:
            dta = await self._redis.get(key)
            if dta is None:
                return None
            print("Cache hit:", key, dta)
            return pickle.loads(dta)
        except Exception:
            print_exc()
            return None

    async def get_ticker_info(self, ticker: str) -> TickerInfo | None:
        key = f"stonks:ticker-info:{ticker}"
        if data := await self._get_cache(key):
            return data

        resp = await self._get(f"/v3/reference/tickers/{ticker.upper()}")
        try:
            resp.raise_for_status()
        except aiohttp.ClientError:
            print(f"Failed to get info for ticker {ticker}.", await resp.text())
            return None

        data = (await resp.json())["results"]
        await self._set_cache(key, data, ex=None)
        print("Ticker info data:", data)
        return data

    async def get_quote(self, ticker: str) -> QuoteResponse:
        key = f"stonks:quote:{ticker}"
        if data := await self._get_cache(key):
            return data

        ticker = ticker.upper()
        params = {"adjusted": "true"}
        today = (datetime.now().date() - timedelta(days=1)).isoformat()
        resp = await self._get(f"/v1/open-close/{ticker}/{today}", params=params)
        data = await resp.json()
        resp.raise_for_status()

        await self._set_cache(key, data)

        return QuoteResponse(**data)

    async def get_time_series(
        self, ticker: str, start_date: str, end_date: str
    ) -> TimeSeriesResponse:
        key = f"stonks:time-series:{ticker}"
        if data := await self._get_cache(key):
            return data

        resp = await self._get(
            f"/v2/aggs/ticker/{ticker.upper()}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc&limit=180"
        )
        resp.raise_for_status()
        data = await resp.json()
        await self._set_cache(key, data)

        return data

    async def create_graph(self, ticker: str, start_date: str, end_date: str):
        data = await self.get_time_series(ticker, start_date, end_date)
        xdata = [
            datetime.fromtimestamp(x["t"] / 1000).date().isoformat()
            for x in data["results"]
        ]
        ydata = [x["c"] for x in data["results"]]

        plt.style.use("dark_background")
        plt.rcParams["figure.figsize"] = (4, 2.3)
        plt.rcParams["font.size"] = 8
        _, ax = plt.subplots()

        ax.plot(xdata, ydata, color="khaki", linewidth=1)
        ax.set_ylabel("Price", color="lightgrey")
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
        ax.xaxis.set_major_formatter(
            mdates.ConciseDateFormatter(mdates.AutoDateLocator())
        )
        ax.tick_params(colors="lightgrey")
        for spine in ax.spines.values():
            spine.set_edgecolor("grey")
        ax.grid(True, alpha=0.4, color="lightgrey")

        file = BytesIO()
        plt.savefig(file, format="webp", bbox_inches="tight")

        return file

    async def close(self):
        if self._owns_session:
            await self._session.close()


def get_date_range(days=180):
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)
    return start_date.isoformat(), end_date.isoformat()


class Stonks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("MASSIVE_API_KEY")

    @commands.command(name="stonk", aliases=["stock", "stocks", "stonks"])
    async def stonk(self, ctx: CustomContext, *, symbol: str):
        """Get current information on a stonk"""
        if not self.api_key:
            return print("Stock (https://massive.com) API key is not set")

        massive = MassiveClient(self.api_key)
        try:
            quote = await massive.get_quote(symbol)
        except aiohttp.ClientError:
            return await ctx.error("Couldn't find a matching stock")

        ticker_info = await massive.get_ticker_info(symbol)
        if ticker_info is None:
            print(f"Found quote but failed to get ticker info for {symbol}")
            return await ctx.error("Couldn't find a matching stock")

        graph = await massive.create_graph(symbol, *get_date_range())
        graph.seek(0)
        graph_file_name = f"{symbol}-{datetime.now().timestamp():.0f}.webp"
        file = discord.File(graph, filename=graph_file_name)
        await massive.close()

        ticker = quote["symbol"]
        name = ticker_info["name"]
        last_price = quote["preMarket"]
        open_ = quote["open"]
        high = quote["high"]
        low = quote["low"]
        change = quote["open"] - quote["close"]
        percent_change = change / quote["open"] * 100
        currency = ticker_info["currency_name"].upper()
        currency_symbol = ticker_info.get("currency_symbol") or "$"

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
            name=f"Last Price ({currency})",
            value=f"{currency_symbol}{last_price:,.2f}",
        )
        em.add_field(
            name="Percent Change",
            value=f"{'⬇️' if percent_change < 0 else '⬆️' if percent_change > 0 else ''} {abs(percent_change):,.2f}%",
            inline=False,
        )
        em.add_field(name="Open", value=f"{currency_symbol}{open_:,.2f}")
        em.add_field(name="High", value=f"{currency_symbol}{high:,.2f}")
        em.add_field(name="Low", value=f"{currency_symbol}{low:,.2f}")
        em.set_footer(text="last updated")
        timestamp = datetime.fromisoformat(quote["from"])
        em.timestamp = datetime(timestamp.year, timestamp.month, timestamp.day, 21)
        em.set_image(url=f"attachment://{graph_file_name}")

        await ctx.send(embed=em, file=file)


async def setup(bot):
    await bot.add_cog(Stonks(bot))


class Address(TypedDict):
    address1: str
    city: str
    postal_code: str
    state: str


class Branding(TypedDict):
    icon_url: str
    logo_url: str


class TickerInfo(TypedDict):
    active: bool
    address: Address
    branding: Branding
    cik: str
    composite_figi: str
    currency_name: str
    description: str
    homepage_url: str
    list_date: str
    locale: str
    market: str
    market_cap: int
    name: str
    phone_number: str
    primary_exchange: str
    round_lot: int
    share_class_figi: str
    share_class_shares_outstanding: int
    sic_code: str
    sic_description: str
    ticker: str
    ticker_root: str
    total_employees: int
    type: str
    weighted_shares_outstanding: int


class Candle(TypedDict):
    c: float  # close
    h: float  # high
    l: float  # low
    n: int  # number trades
    o: float  # open
    t: int  # time of aggregate window start
    v: int  # volume
    vw: float  # volume weighted average price


class TimeSeriesResponse(TypedDict):
    adjusted: bool
    next_url: str
    queryCount: int
    request_id: str
    results: list[Candle]
    resultsCount: int
    status: str
    ticker: str


QuoteResponse = TypedDict(
    "QuoteResponse",
    {
        "status": str,
        "from": str,
        "symbol": str,
        "open": float,
        "high": float,
        "low": float,
        "close": float,
        "volume": float,
        "afterHours": float,
        "preMarket": float,
    },
)


class QuoteNotFoundResponse(TypedDict):
    status: str
    request_id: str
    message: str
