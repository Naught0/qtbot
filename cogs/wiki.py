import discord
from discord.ext import commands

from urllib.parse import quote_plus
from utils import aiohttp_wrap as aw


class Wiki(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.search_uri = (
            "http://en.wikipedia.org/w/api.php?action=opensearch&format=json&search={}&limit=1&namespace=0"
        )
        self.random_uri = "https://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1"
        self.headers = {
            "user-agent": "qtbot/1.0 - A friendly discord bot (https://github.com/Naught0/qtbot)"
        }
        self.aio_session = bot.aio_session

    @commands.command(name="wiki", aliases=["wi"])
    async def wiki_search(self, ctx, *, query=None):
        """ Get the closest matching Wikipedia article for a given query """

        # Determine whether we want a random article
        if not query:
            random_response = await aw.aio_get_json(
                self.aio_session, self.random_uri, headers=self.headers
            )
            query = random_response["query"]["random"][0]["title"]

        # Spaces -> +
        formatted_query = quote_plus(query)

        # Get wiki page
        wiki_info = await aw.aio_get_json(
            self.aio_session,
            self.search_uri.format(formatted_query),
            headers=self.headers,
        )

        # No result found
        if not wiki_info[1]:
            return await ctx.send(f"Sorry, I couldn't find anything for `{query}`.")

        # Create embed
        em = discord.Embed(title=wiki_info[1][0], color=discord.Color.blue())
        if wiki_info[2][0] == "":
            em.description = "Disambiguation / Redirect Page"
        else:
            em.description = wiki_info[2][0]
        em.url = wiki_info[3][0]
        em.set_thumbnail(
            url="https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300"
        )

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
