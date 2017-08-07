#!/bin/env python

import discord
import wolframalpha
import json
from discord.ext import commands


class Calculator:
    def __init__(self, bot):
        self.bot = bot

    with open("data/apikeys.json", "r") as f:
        api_key = json.load(f)["wolfram"]

    client = wolframalpha.Client(api_key)

    @commands.command(aliases=['calc', 'cal', 'c'])
    async def calculate(self, ctx, *args):
        """ Calculate like, anything. """

        if not args:
            return await ctx.send("Please enter something for me to calculate!")

        q = " ".join(args)
        result = Calculator.client.query(q)

        # Try to calculate
        try:
            await ctx.send(next(result.results).text)
        except AttributeError:  # Except when no result
            await ctx.send("Sorry, I couldn't calculate `{}`.".format(q))


def setup(bot):
    bot.add_cog(Calculator(bot))
