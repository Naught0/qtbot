import discord
from discord.ext import commands

from urllib.parse import quote_plus
from utils import aiohttp_wrap as aw


class Wiki(commands.Cog):
    SUMMARY_URI = "https://en.wikipedia.org/api/rest_v1/page/summary/{}?redirect=true"
    SEARCH_URI = "http://en.wikipedia.org/w/api.php?action=opensearch&format=json&search={}&limit=1&namespace=0"
    HEADERS = {
        "user-agent": "qtbot/1.0 - A friendly discord bot (https://github.com/Naught0/qtbot)"
    }

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session

    @commands.command(name="wiki", aliases=["wi"])
    async def wiki_search(self, ctx, *, query=None):
        """ Get the closest matching Wikipedia article for a given query """
        formatted_query = quote_plus(query)

        # Get wiki page
        wiki_info = await aw.aio_get_json(
            self.session,
            self.SEARCH_URI.format(formatted_query),
            headers=self.HEADERS,
        )

        # No result found
        if not wiki_info[1]:
            return await ctx.error(f"Sorry, I couldn't find anything for `{query}`.")

        # Get summary
        article_title = quote_plus(wiki_info[1][0].replace(" ", "_"), safe="_")
        article_summary = await aw.aio_get_json(
            self.session, self.SUMMARY_URI.format(article_title), headers=self.HEADERS
        )
        # Create embed
        em = discord.Embed(title=article_title, color=discord.Color.blurple())
        em.description = article_summary["extract"]
        em.url = article_summary["content_urls"]["desktop"]["page"]
        em.set_thumbnail(
            url="https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300"
        )

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
