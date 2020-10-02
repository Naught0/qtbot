import discord
import random

from dateutil.parser import parse
from urllib.parse import quote_plus
from discord.ext import commands
from discord.utils import escape_markdown
from utils.aiohttp_wrap import aio_get_json


class Trump(commands.Cog):
    """ A cog which nobody ever asked for, that fetches a random Trump tweet """

    RAND_URL = "https://api.tronalddump.io/random/quote"
    SEARCH_URL = "https://api.tronalddump.io/search/quote"
    PIC_URL = "https://www.tronalddump.io/img/tronalddump_850x850.png"

    @commands.command(name="trump", aliases=["tt"])
    async def _trump(self, ctx: commands.Context, *, query: str = None):
        """Get a random, dumb Trump quote -- alternatively, search for something similarly stupid he's said

        Args:
            ctx (commands.Context): Message context
            query (str, optional): Optional query. Defaults to None.
        """
        if query:
            search_results = await aio_get_json(
                ctx.bot.aio_session,
                self.SEARCH_URL,
                params={"query": quote_plus(query)},
            )
            if search_results is None:
                return await ctx.error(
                    "Couldn't communicate with our dear leader",
                    description="Please try again later -- or don't.",
                )
            if search_results["count"] == 0:
                return await ctx.error(
                    "No results",
                    description=f"Couldn't find any Trumpisms on `{escape_markdown(query)}`",
                )
            
            resp = random.choice(search_results["_embedded"]["quotes"])
        else:
            resp = await aio_get_json(ctx.bot.aio_session, self.RAND_URL)
        
        em = discord.Embed(color=0x00acee)
        em.set_author(name="Donald Trump", icon_url=self.PIC_URL, url=resp["source"]["url"])
        em.description = resp["value"]
        em.timestamp = parse(resp["appeared_at"])
        em.set_footer(text="via twitter", icon_url="https://i.imgur.com/DUUkDwY.png")


def setup(bot):
    bot.add_cog(Trump(bot))
