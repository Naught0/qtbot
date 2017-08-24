import discord
import json
from discord.ext import commands
from wordnik import *
import urbandictionary as urbdic


class Dictionary:
    def __init__(self, bot):
        self.bot = bot

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

        await ctx.send('{} _{}_ `{}`'.format(word.title(), word_pos, final_result.text))

    # Urban dictionary
    @commands.command(name='ud')
    async def get_urban_def(self, ctx, *, word):
        """ Consult the world's leading dictionary """
        result = urbdic.define(word)

        if not result:
            return await ctx.send("Sorry, couldn't find that one.")

        await ctx.send('{}: `{}`'.format(word.title(), result[0].definition))


def setup(bot):
    bot.add_cog(Dictionary(bot))
