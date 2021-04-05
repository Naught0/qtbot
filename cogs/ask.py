import asyncio
from typing import List

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.utils import escape_markdown

from utils import aiohttp_wrap as aw


class Google(commands.Cog):
    SEARCH_URI = "https://duckduckgo.com/html/"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/41.0.2228.0 Safari/537.36"
    }
    # EMOJIS = [f"{x}\U000020e3" for x in range(1, 10)]

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis = bot.redis_client

    @commands.group(
        invoke_without_command=True, name="google", aliases=["g", "ddg", "ask"]
    )
    async def _google(self, ctx, *, query: str = None):
        """ Get search results from [REDACTED], now that Google hates me. """
        if query is None or query.strip() == "":
            return await ctx.error("Feel free to search something")

        resp = await aw.aio_get_text(
            self.session, headers=self.HEADERS, params={"q": query}
        )

        soup = BeautifulSoup(resp, 'lxml')
        links = [x['href'] for x in soup.find_all('a', {'class': 'result__a'})]
        if len(links) == 0:
            return await ctx.error(f"Sorry, couldn't find anything for `{escape_markdown(query)}`")
        
        ctx.send(f"**Top Result:**\n{links[0]}\n**See Also:**\n1. <{links[1]}>\n2. <{links[2]}>")


def setup(bot):
    bot.add_cog(Google(bot))
