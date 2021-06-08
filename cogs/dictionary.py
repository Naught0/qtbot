import json
import re
from urllib.parse import quote_plus

import discord
from discord.ext import commands
from asyncurban import UrbanDictionary, WordNotFoundError

from utils import aiohttp_wrap as aw


class Dictionary(commands.Cog):
    URL = "https://dictionaryapi.com/api/v3/references/collegiate/json/{}"

    def __init__(self, bot):
        self.session = bot.aio_session
        self.urban = UrbanDictionary(loop=bot.loop, session=self.session)
        with open(bot.config_file) as f:
            self.dictionary_key = json.load(f)["webster"]

    # Returns the most common definition of a word
    @commands.command(name="define", aliases=["d", "def", "dictionary", "dict", "dic"])
    async def _define(self, ctx, *, word: str):
        """Provides the definition of a word"""
        query = quote_plus(word)
        resp = await aw.aio_get_json(
            self.session,
            self.URL.format(query),
            params={"key": self.dictionary_key},
        )
        if resp is None:
            return await ctx.error(f"Couldn't find anything on `{word}`")

        # Grab the first three defn's, combine to string w/ bullet points
        definitions = "\n".join([f"\u2022 {x}" for x in resp[0]["shortdef"][:3]])

        em = discord.Embed(color=discord.Color.blurple())
        em.set_author(
            name=f"{word.title()} - ({resp[0]['fl']})",
            url=f"https://merriam-webster.com/dictionary/{query}",
            icon_url="https://i.imgur.com/9jO7EYk.png",
        )
        em.description = definitions
        em.set_footer(text=f"Originated ~{re.sub(r'{.+', '', resp[0]['date'])}")
        await ctx.send(embed=em)

    @commands.command(name="urban", aliases=["ud", "urband"])
    async def _urban(self, ctx, *, word: str = None):
        """Consult the world's leading dictionary or get a random word by searching nothing"""
        try:
            if word is None:
                result = await self.urban.get_random()
            else:
                result = await self.urban.get_word(word)
        except WordNotFoundError:
            return await ctx.error(f"Couldn't find anything on `{word}`")
        except ConnectionError:
            return await ctx.error(f"Sorry, the UrbanDictionary API died")

        em = discord.Embed(color=discord.Color.blurple())
        em.set_author(
            name=result.word.title(),
            url=result.permalink,
            icon_url="https://i.imgur.com/nzyqrIj.png",
        )
        em.description = result.definition
        em.set_footer(text=f"from user {result.author}")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Dictionary(bot))
