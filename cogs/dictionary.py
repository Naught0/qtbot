import discord
import json
import AsyncUrban
from discord.ext import commands
from asyncurban import UrbanDictionary, WordNotFoundError
from wordnik import *


class Dictionary:
    def __init__(self, bot):
        self.bot = bot
        self.urban = UrbanDictionary(loop=bot.loop, session=bot.aio_session)

    # Load API key
    with open('data/apikeys.json') as f:
        apiKeys = json.load(f)

    # Init wordnik objects
    wordnikKey = apiKeys['wordnik']
    WordClient = swagger.ApiClient(wordnikKey, 'http://api.wordnik.com/v4')

    # Returns the most common definition of a word
    @commands.command(name='define', aliases=['d'])
    async def wordnik_define(self, ctx, *, word):
        """ Provides the definition of a word """
        wordApi = WordApi.WordApi(Dictionary.WordClient)

        parts_of_speech = {'noun': 'n.', 'verb': 'v.', 'adjective': 'adj.', 'adverb': 'adv.',
                           'interjection': 'interj.', 'conjunction': 'conj.', 'preposition': 'prep.', 'pronoun': 'pron.'}

        result = wordApi.getDefinitions(word)

        if not result:
            return await ctx.send("Sorry, couldn't find that one.")

        final_result = result[0]

        for pos in parts_of_speech:
            if pos in final_result.partOfSpeech.split('-'):
                word_pos = parts_of_speech[pos]
                break
            else:
                word_pos = final_result.partOfSpeech

        await ctx.send(f'{word.title()} _{word_pos}_ `{final_result.text}`')

    @commands.group(invoke_without_subcommand=True, name='urbdic', aliases=['ud'])
    async def urban_dictionary(self, ctx, *, word):
        """ Consult the world's leading dictionary """
        try:
            result = await self.urban.get_word(word)
        except WordNotFoundError:
            return await ctx.send(f"Sorry, couldn't find anything on `{word}`.")
        except ConnectionError:
            return await ctx.send(f"Sorry, the UrbanDictionary API buggered off.")

        await ctx.send(f'{word.title()}: `{result.definition}`')

    @urban_dictionary.command(name='random', aliases=['-r', 'rand'])
    async def _random(self, ctx):
        """ Get a random word from UrbanDictionary """
        word = await self.urban.get_random()

        await ctx.send(f'{word.title()}: `{word.definition}`')


def setup(bot):
    bot.add_cog(Dictionary(bot))
