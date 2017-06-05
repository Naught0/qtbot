import discord, json
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
    @commands.bot.command()
    async def define(self, word):
        """ Provides the definition of _a_ word """
        self.wordApi = WordApi.WordApi(Dictionary.WordClient)

        self.result = self.wordApi.getDefinitions(word)

        if not self.result:
            return await self.bot.say("Sorry, couldn't find that one.")

        return await self.bot.say("{0}: `{1}`".format(word.title(), self.result[0].text))

    # Urban dictionary
    @commands.bot.command()
    async def ud(self, *args):
        """ Consult the world's leading dictionary """
        self.result = urbdic.define(" ".join(args))

        if not self.result:
            return await self.bot.say("Sorry, couldn't find that one.") 

        return await self.bot.say("{0}: `{1}`".format(" ".join(args).title(), self.result[0].definition))

def setup(bot):
    bot.add_cog(Dictionary(bot))