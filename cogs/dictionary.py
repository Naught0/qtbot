import json
from urllib.parse import quote_plus
from types import SimpleNamespace

import discord
from discord.ext import commands
from asyncurban import UrbanDictionary, WordNotFoundError

from utils import aiohttp_wrap as aw


class Dictionary(commands.Cog):
    WORDNIK_URL = "https://api.wordnik.com/v4/word.json/{}/definitions"
    HEADERS = {"Accept": "application/json"}

    def __init__(self, bot):
        self.PARAMS = {
            "limit": 1,
            "includeRelated": "false",
            "useCanonical": "true",
            "includeTags": "false",
            "api_key": bot.api_keys["wordnik"],
            "sourceDictionaries": "ahd,webster,century,wordnet"
        }
        self.bot = bot
        self.urban = UrbanDictionary(loop=bot.loop, session=bot.aio_session)

    # Returns the most common definition of a word
    @commands.command(name="define", aliases=["d"])
    async def _define(self, ctx, *, word: str):
        """ Provides the definition of a word """

        query = quote_plus(word)
        resp = await aw.aio_get_json(
            self.bot.aio_session,
            self.WORDNIK_URL.format(query),
            params=self.PARAMS,
            headers=self.HEADERS,
        )
        if resp is None:
            return await ctx.error(f"Couldn't find anything on `{word}`")

        result = SimpleNamespace(**resp[0])

        em = discord.Embed(color=discord.Color.blurple())
        em.set_author(
            name=word.title(),
            url=result.wordnikUrl,
            icon_url="https://i.imgur.com/9jO7EYk.png",
        )
        em.description = f"_{result.partOfSpeech}_\n{result.text}"
        em.set_footer(text=result.attributionText)
        await ctx.send(embed=em)

    @commands.group(
        invoke_without_subcommand=True, name="urban", aliases=["ud", "urband"]
    )
    async def _urban(self, ctx, *, word: str = None):
        """ Consult the world's leading dictionary or get a random word by searching nothing"""
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
