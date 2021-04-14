import asyncio
from typing import List

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.utils import escape_markdown

from utils import aiohttp_wrap as aw


class Google(commands.Cog):
    SEARCH_URI = "https://duckduckgo.com/html/"
    IMAGE_URI = "https://bing.com/images/search"
    IE6_HEADERS = {
        "user-agent": "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)"
    }
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/41.0.2228.0 Safari/537.36"
    }
    EMOJIS = [f"{x}\U000020e3" for x in range(1, 10)]

    def __init__(self, bot: commands.Bot):
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
            self.session, self.SEARCH_URI, headers=self.HEADERS, params={"q": query}
        )

        soup = BeautifulSoup(resp, "lxml")
        links = [x["href"] for x in soup.find_all("a", {"class": "result__a"})]
        if len(links) == 0:
            return await ctx.error(
                f"Sorry, couldn't find anything for `{escape_markdown(query)}`"
            )

        await ctx.send(
            f"**Top Result:**\n{links[0]}\n**See Also:**\n1. <{links[1]}>\n2. <{links[2]}>"
        )

    @staticmethod
    def link_to_embed(query: str, link: str) -> discord.Embed:
        em = discord.Embed(title=query)
        em.set_image(url=link)
        return em

    @_google.command(name="-image", aliases=["-i", "-images"])
    async def images(self, ctx: commands.Context, *, query: str = None):
        """Search for images"""
        if query is None or query.strip() == "":
            return await ctx.error("Feel free to search for something")

        resp = await aw.aio_get_text(
            self.session, self.IMAGE_URI, headers=self.IE6_HEADERS, params={"q": query}
        )
        soup = BeautifulSoup(resp, "lxml")
        embeds = [
            self.link_to_embed(query, x["href"])
            for x in soup.find_all("a", {"class": "thumb"})[:5]
        ]

        msg = await ctx.send(embed=embeds[0])

        for x in self.EMOJIS[: len(embeds)]:
            await msg.add_reaction(x)

        while True:
            try:
                reaction, _ = await self.bot.wait_for(
                    "reaction_add",
                    timeout=30.0,
                    check=lambda reaction, user: (
                        user == ctx.author
                        and reaction.emoji in self.EMOJIS
                        and reaction.message.id == msg.id
                    ),
                )
            except asyncio.TimeoutError:
                return await msg.clear_reactions()

            if reaction.emoji in self.EMOJIS:
                await msg.edit(embed=embeds[self.EMOJIS.index(reaction.emoji)])
                await msg.remove_reaction(reaction.emoji, ctx.author)


def setup(bot):
    bot.add_cog(Google(bot))
