import discord
import re

from bs4 import BeautifulSoup
from dateutil.parser import parse as parse_date
from discord.ext import commands
from discord.utils import escape_markdown
from utils.aiohttp_wrap import aio_get_text


class Stonks(commands.Cog):
    URL = "https://bigcharts.marketwatch.com/quickchart/quickchart.asp"
    TTL = 60 * 15

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis_client = bot.redis_client

    @commands.command(name="stonk", aliases=["stock", "stocks", "stonks"])
    async def stonk(self, ctx: commands.Context, *, symbol: str):
        """Get current information on a stonk"""
        html = await aio_get_text(self.session, self.URL, params={"symb": symbol})
        soup = BeautifulSoup(html, "lxml")
        if (
            soup.select_one("caption.shaded")
            and "unable to find" in soup.select_one("caption.shaded").text
        ):
            return await ctx.error(
                f"Could not find security, fund, or index matching: `{escape_markdown(symbol)}`"
            )

        em = discord.Embed(
            title=f"{soup.select_one('.header .fleft:nth-child(2)').text} - {soup.select_one('.header .fleft').text.strip()}"
        )
        em.url = f"https://finance.yahoo.com/quote/{symbol}"
        em.add_field(
            name="Last Price $USD",
            value=f"${float(soup.select_one('.last > div').text.strip().replace(',', '')):.2f}",
        )
        percent_change = soup.select_one(".change:nth-child(1) div").text.strip()
        em.add_field(
            name="Percent Change",
            value=f"{'⬇️' if '-' in percent_change else '⬆️'} {re.sub('[-+]', '', percent_change)}",
            inline=False,
        )
        em.add_field(
            name="Open",
            value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(3) > div').text}",
        )
        em.add_field(
            name="High",
            value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(4) > div').text}",
        )
        em.add_field(
            name="Low",
            value=f"${soup.select_one('tr:nth-child(3) > td:nth-child(5) > div').text}",
        )
        em.set_footer(text="last updated")
        em.timestamp = parse_date(f"{soup.select_one('.soft.time').text} -0400")
        em.set_image(url=soup.select_one(".vatop img")["src"])

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Stonks(bot))
