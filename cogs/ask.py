import os

import discord
from bs4 import BeautifulSoup
from discord.ext import commands
from discord.utils import escape_markdown, escape_mentions

from lib.image_search import ImageSearch, LightImageResult
from utils import aiohttp_wrap as aw
from utils.custom_context import CustomContext
from utils.paginate import paginate


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
        self.image_search = ImageSearch(self.session, os.environ["serpapi_api_key"])

    @commands.group(
        invoke_without_command=True, name="google", aliases=["g", "ddg", "ask"]
    )
    async def _google(self, ctx, *, query: str = ""):
        """Get search results from [REDACTED], now that Google hates me."""
        if not query.strip():
            return await ctx.error("Feel free to search something")

        resp = await aw.aio_get_text(
            self.session, self.SEARCH_URI, headers=self.HEADERS, params={"q": query}
        )

        soup = BeautifulSoup(resp, "lxml")
        links = [
            x["href"]
            for x in soup.find_all("a", {"class": "result__a"})
            if "y.js" not in x["href"]
        ]
        if len(links) == 0:
            return await ctx.error(
                f"Sorry, couldn't find anything for `{escape_markdown(query)}`"
            )

        await ctx.send(
            f"**Top Result:**\n{links[0]}\n**See Also:**\n1. <{links[1]}>\n2. <{links[2]}>"
        )

    @_google.command(name="-image", aliases=["-i", "-images"])
    async def images(self, ctx: CustomContext, *, query: str = ""):
        """Search for images"""
        if not query.strip():
            return await ctx.error("Feel free to search for something")

        results = (await self.image_search.search(query))["images_results"]
        embeds = [create_image_embed(query, r) for r in results[:8]]
        msg = await ctx.send(embed=embeds[0])
        await paginate(ctx, msg, embeds)


def create_image_embed(query: str, result: LightImageResult):
    em = discord.Embed(
        title=f"Results for {escape_mentions(escape_markdown(query))}",
        description=f"[{result['title']}]({result['link']})",
        color=discord.Color.blurple(),
    )
    em.set_image(url=result["original"])

    return em


async def setup(bot):
    await bot.add_cog(Google(bot))
