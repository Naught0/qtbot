import discord
import wolframalpha
import json
from discord.ext import commands


class Calculator():
    def __init__(self, bot):
        self.bot = bot

    with open("data/apikeys.json", "r") as f:
        apiKeys = json.load(f)

    client = wolframalpha.Client(apiKeys["wolfram"])

    @commands.bot.command(aliases=['calc', 'cal', 'c'])
    async def calculate(self, *args):
        """ Calculate like, anything. """

        q = " ".join(args)
        result = Calculator.client.query(q)

        # Try to calculate
        try:
            return await self.bot.say(next(result.results).text)
        except AttributeError:  # Except when no result
            return await self.bot.say("Sorry, I couldn't calculate `{}`.".format(q))


def setup(bot):
    bot.add_cog(Calculator(bot))
