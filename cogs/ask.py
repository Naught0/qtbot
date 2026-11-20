import os

import discord
from discord.ext import commands
from discord.utils import escape_markdown, escape_mentions

from lib.google_search import GoogleSearch
from lib.image_search import ImageSearch, LightImageResult
from utils.custom_context import CustomContext
from utils.paginate import paginate


class Google(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis = bot.redis_client
        api_key = os.environ["SERPAPI_API_KEY"]
        self.image_search = ImageSearch(self.session, api_key)
        self.google_search = GoogleSearch(self.session, api_key)

    @commands.group(
        invoke_without_command=True, name="google", aliases=["g", "ddg", "ask"]
    )
    async def _google(self, ctx, *, query: str = ""):
        """Get search results from Google, now that Google hates me."""
        if not query.strip():
            return await ctx.error("Feel free to search something")

        results = (await self.google_search.search(query)).get("organic_results", [])
        if len(results) == 0:
            return await ctx.error(
                f"Sorry, couldn't find anything for `{escape_markdown(query)}`"
            )

        message = f"**Top Result:**\n{results[0]['link']}"
        see_also = "\n".join(
            f"{i}. <{result['link']}>" for i, result in enumerate(results[1:3], start=1)
        )
        if see_also:
            message += f"\n**See Also:**\n{see_also}"

        await ctx.send(message)

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
