import re
from collections.abc import Mapping

import discord
from aiohttp import ClientSession
from dateutil.parser import parse as parse_date
from discord.ext import commands

from utils.custom_context import CustomContext


class MissingEntitlementToken(Exception): ...


async def get_entitlement_token(session: ClientSession) -> str | None:
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


async def fetch_wsj_data(session: ClientSession, ticker: str) -> dict | None:
    entitlement_token = await get_entitlement_token(session)
    if entitlement_token:
        ckey = entitlement_token[:10]
        quote_data = await get_quote_data(session, ticker, entitlement_token, ckey)
        return quote_data["InstrumentResponses"][0]["Matches"][0]
    else:
        return None


class Stonks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session

    @commands.command(name="stonk", aliases=["stock", "stocks", "stonks"])
    async def stonk(self, ctx: CustomContext, *, symbol: str):
        """Get current information on a stonk"""
        resp = await fetch_wsj_data(self.session, symbol)
        if not resp:
            return await ctx.error("Couldn't find a matching stock")

        ticker = resp["Instrument"]["Ticker"]
        name = resp["Instrument"]["CommonName"]
        price_data = resp["CompositeTrading"]
        last_price = price_data["Last"]["Price"]["Value"]
        currency = price_data["Last"]["Price"]["Iso"]
        open = price_data["Open"]["Price"]["Value"]
        high = price_data["High"]["Price"]["Value"]
        low = price_data["Low"]["Price"]["Value"]
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
        em.add_field(name="Open", value=f"${open:,.2f}")
        em.add_field(name="High", value=f"${high:,.2f}")
        em.add_field(name="Low", value=f"${low:,.2f}")
        em.set_footer(text="last updated")
        em.timestamp = parse_date(price_data["Last"]["Time"])

        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Stonks(bot))
