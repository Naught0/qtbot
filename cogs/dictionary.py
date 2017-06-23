import discord
import json
from discord.ext import commands
from wordnik import *
import urbandictionary as urbdic


class Dictionary():
    def __init__(self, bot):
        self.bot = bot

    # Load API key
    with open("data/apikeys.json", "r") as f:
        apiKeys = json.load(f)
    f.close()

    # Init wordnik objects
    wordnikKey = apiKeys["wordnik"]
    WordClient = swagger.ApiClient(wordnikKey, 'http://api.wordnik.com/v4')

    # Returns the most common definition of a word
    @commands.bot.command(aliases=['def', 'd'])
    async def define(self, word):
        """ Provides the definition of _a_ word """
        wordApi = WordApi.WordApi(Dictionary.WordClient)

        result = wordApi.getDefinitions(word)

        if not result:
            return await self.bot.say("Sorry, couldn't find that one.")

        return await self.bot.say("{0}: `{1}`".format(word.title(), result[0].text))

    # Urban dictionary
    @commands.bot.command(aliases=['ud', 'urbdic'])
    async def urbanDictionary(self, *args):
        """ Consult the world's leading dictionary """
        result = urbdic.define(" ".join(args))

        if not result:
            return await self.bot.say("Sorry, couldn't find that one.")

        return await self.bot.say("{0}: `{1}`".format(" ".join(args).title(), result[0].definition))


def setup(bot):
    bot.add_cog(Dictionary(bot))
