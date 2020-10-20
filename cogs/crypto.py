import json
import time
import discord

import dateutil.parser
from discord.ext import commands
from discord.utils import escape_markdown

from utils import aiohttp_wrap as aw


class Crypto(commands.Cog):
    """ Allows users to track bitcoin and other currencies (eventually) """

    URL_BTC = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
    CACHE_TTL = 10 * 60

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis = bot.redis_client
        self.HEADERS = {"X-CMC_PRO_API_KEY": bot.api_keys["cmc"]}

        with open("data/cmc_mappings.json") as f:
            self._mappings = json.load(f)

        self.cmc_map = {
            frozenset([entry["name"].lower(), entry["symbol"].lower()]): entry["id"]
            for entry in self._mappings["data"]
        }

    @commands.command(name="crypto", aliases=["cry", "btc"])
    async def _crypto(self, ctx: commands.Context, *, currency: str = "btc"):
        """Get price and trend information for a cryptocurrency
        You can refer to a currency by its symbol or full name
        Defaults to BTC if no currency is supplied"""
        currency = currency.lower()

        if len(currency) < 3:
            return await ctx.error(
                "Unrecognized currency",
                description="Please use the full currency name or symbol, e.g. `eth` or `ethereum`",
            )

        currency_id = None
        for item in self.cmc_map:
            if set([currency]) & item:
                currency_id = self.cmc_map[item]

        if currency_id == None:
            return await ctx.error(
                "Unrecognized currency",
                description=f"Couldn't find anything for `{escape_markdown(currency)}`",
            )

        redis_key = "crypto"
        if await self.redis.exists(redis_key):
            resp = json.loads(await self.redis.get(redis_key))

        # Make a single request for top 25 endpoints and cache
        else:
            resp = (
                await aw.aio_get_json(
                    self.session,
                    self.URL_BTC,
                    headers=self.HEADERS,
                    params={"id": ",".join([str(x) for x in self.cmc_map.values()])},
                )
            )["data"]

            await self.redis.set(redis_key, json.dumps(resp), ex=self.CACHE_TTL)

        crypto_info = resp[str(currency_id)]

        em = discord.Embed(color=0xF7931A)
        em.set_author(
            name=f"{crypto_info['name']} ({crypto_info['symbol']})",
            icon_url=f"https://s3.coinmarketcap.com/static/img/coins/64x64/{currency_id}.png",
        )
        em.add_field(
            name="Price $USD",
            value=f"${crypto_info['quote']['USD']['price']:,.2f}",
            inline=False,
        )
        em.set_footer(text="Last updated")
        em.timestamp = dateutil.parser.parse(crypto_info["last_updated"])

        # Hourly trend
        change_1h = crypto_info["quote"]["USD"]["percent_change_1h"]
        change_1h_str = (
            f":arrow_up: {change_1h:.2f}%"
            if "-" not in str(change_1h)
            else f":arrow_down: {change_1h:.2f}%"
        )
        em.add_field(name="Hourly trend", value=change_1h_str)

        # Daily trend
        change_24h = crypto_info["quote"]["USD"]["percent_change_24h"]
        change_24h_str = (
            f":arrow_up: {change_24h:.2f}%"
            if "-" not in str(change_24h)
            else f":arrow_down: {change_24h:.2f}%"
        )
        em.add_field(name="Daily trend", value=change_24h_str)

        # Weekly trend
        change_7d = crypto_info["quote"]["USD"]["percent_change_7d"]
        change_7d_str = (
            f":arrow_up: {change_7d:.2f}%"
            if "-" not in str(change_7d)
            else f":arrow_down: {change_7d:.2f}%"
        )
        em.add_field(name="Weekly trend", value=change_7d_str)

        # Ticker graph
        em.set_image(
            url=f"https://s3.coinmarketcap.com/generated/sparklines/web/7d/usd/{currency_id}.png?{int(time.time())}"
        )

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Crypto(bot))
