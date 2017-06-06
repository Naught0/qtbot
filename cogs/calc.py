import discord, wolframalpha, json
from discord.ext import commands

class Calculator():
    def __init__(self, bot):
        self.bot = bot

    with open("data/apikeys.json", "r") as f:
        apiKeys = json.load(f)

    client = wolframalpha.Client(apiKeys["wolfram"])

    @commands.bot.command(aliases = ['calc', 'cal', 'c'])
    async def calculate(self, *args):
        """ Calculate like, anything """
        self.q = " ".join(args)
        self.result = Calculator.client.query(self.q)

        return await self.bot.say(next(self.result.results).text)

def setup(bot):
    bot.add_cog(Calculator(bot))