import discord
import json
import io
import re
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from dateutil.rrule import rrule, DAILY
from datetime import datetime, timedelta
from discord.ext import commands
from discord.utils import escape_markdown
from utils.aiohttp_wrap import aio_get_json, aio_get_text


class Stonks(commands.Cog):
    URL = "https://bigcharts.marketwatch.com/quickchart/quickchart.asp"
    TTL = 60 * 15

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis_client = bot.redis_client
        self.headers = {"X-Finnhub-Token": bot.api_keys["stonks"]}
        with open("data/apikeys.json") as f:
            keys = json.load(f)
            self.av_key = keys["alpha_vantage"]
            self.api_key = keys["stonks"]

    @commands.command(name="stronk", hidden=True) #aliases=["stock", "stocks", "stonks"])
    async def stronks(self, ctx: commands.Context, *, symbol: str):
        """Get current information on a stonk"""
        html = await aio_get_text(self.session, self.URL, params = {"symb": symbol})
        soup = BeautifulSoup(html, 'lxml')
        if soup.select_one('caption.shaded') and 'unable to find' in soup.select_one('caption.shaded').text:
            return await ctx.error(f"Could not find security, fund, or index matching: `{escape_markdown(symbol)}`")
        
        em = discord.Embed(title=f"{soup.select_one('.header .fleft:nth-child(2)').text} - {soup.select_one('.header .fleft').text.strip()}")
        em.url = f"https://finance.yahoo.com/quote/{symbol}"
        em.add_field(name="Last Price $USD", value=f"${float(soup.select_one('.last > div').text.strip()):.2f}", inline=False)
        percent_change = soup.select_one('.change:nth-child(1) div').text.strip()
        em.add_field(name="Percent Change", value=f"{'⬇️' if '-' in percent_change else '⬆️'} {re.sub('[-+]', '', percent_change)}")
        em.add_field(name="Open", value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(3) > div').text}")
        em.add_field(name="High", value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(4) > div').text}")
        em.add_field(name="Low", value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(5) > div').text}")
        em.set_footer(text="last updated")
        em.timestamp = parse_date(f"{soup.select_one('.soft.time').text} -0400")
        em.set_image(url=soup.select_one('.vatop img')['src'])

        await ctx.send(embed=em)

    @commands.command(name="stonk", aliases=["stonks", "stock", "stocks"])
    async def stonks(self, ctx: commands.Context, *, symbol: str):
        if len(symbol) > 5:
            return await ctx.error(
                "Stock error",
                description=f"Invalid ticker symbol: `{escape_markdown(symbol)}`",
            )

        symbol = symbol.upper()
        params = {"symbol": symbol, "apikey": self.av_key, "function": "GLOBAL_QUOTE"}

        redis_key = f"stonks:{symbol}"
        if await self.redis_client.exists(redis_key):
            resp = json.loads(await self.redis_client.get(redis_key))
        else:
            resp = await aio_get_json(self.session, self.URL, params=params)

            if resp is None:
                return await ctx.error(
                    "API Error",
                    description="There was an issue with the stocks API, try again later",
                )

            if not resp["Global Quote"]:
                return await ctx.error(
                    "Stock error",
                    description=f"Couldn't find any stock information for `{symbol}`",
                )

            graph_params = {
                "function": "TIME_SERIES_DAILY",
                "apikey": self.av_key,
                "symbol": symbol,
            }
            graph_resp = (
                await aio_get_json(self.session, self.URL, params=graph_params)
            )["Time Series (Daily)"]

            company_profile = await aio_get_json(
                self.session,
                self.PROFILE_URL,
                params={"symbol": symbol},
                headers={"X-Finnhub-Token": self.api_key},
            )
            resp["company_profile"] = company_profile
            resp["historical_data"] = graph_resp

            await self.redis_client.set(redis_key, json.dumps(resp), ex=self.TTL)

        if resp["company_profile"]:
            name = f"{resp['company_profile']['name']} ({symbol})"
        else:
            name = symbol

        if "logo" in resp["company_profile"] and resp["company_profile"]["logo"] != "":
            icon = resp["company_profile"]["logo"]
        else:
            if float(resp["Global Quote"]["09. change"]) < 0:
                icon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/twitter/259/chart-decreasing_1f4c9.png"
            else:
                icon = "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/twitter/259/chart-increasing_1f4c8.png"

        # Create the graph

        today = datetime.today().date()
        start_date = today - timedelta(days=45)
        series = []
        for dt in rrule(DAILY, dtstart=start_date, until=today):
            d = dt.strftime("%Y-%m-%d")
            if d in resp["historical_data"]:
                series.append(float(resp["historical_data"][d]["4. close"]))
            else:
                continue

        graph_image = io.BytesIO()
        plt.figure(figsize=(16, 9))
        plt.plot(series, linewidth=12, color="gold", solid_capstyle="round")
        plt.axis("off")
        plt.savefig(graph_image, format="png", transparent=True, dpi=10)
        graph_image.seek(0)
        file = discord.File(graph_image, filename=f"{symbol}.png")

        percent_change = float(resp["Global Quote"]["09. change"])
        if percent_change > 0:
            emoji = ":arrow_up:"
        elif percent_change < 0:
            emoji = ":arrow_down:"
        else:
            emoji = ":arrow_right:"

        em = discord.Embed(color=discord.Color.blurple())
        em.set_author(
            name=name,
            icon_url=icon,
            url=resp["company_profile"]["weburl"]
            if "weburl" in resp["company_profile"]
            else "",
        )
        em.add_field(
            name="Current Price",
            value=f"${float(resp['Global Quote']['05. price']):,.2f}",
            inline=False,
        )
        em.add_field(
            name="Previous Close",
            value=f"${float(resp['Global Quote']['08. previous close']):,.2f}",
        )
        em.add_field(
            name="% Change Today",
            value=f"{emoji} {resp['Global Quote']['10. change percent']}",
        )

        em.set_image(url=f"attachment://{symbol}.png")

        em.set_footer(text="Last updated")
        em.timestamp = ctx.message.created_at

        await ctx.send(file=file, embed=em)

        plt.close()


def setup(bot):
    bot.add_cog(Stonks(bot))
