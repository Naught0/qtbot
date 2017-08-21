#!/bin/env python

import discord
import wolframalpha
import json
from discord.ext import commands


class Calculator:
    def __init__(self, bot):
        self.bot = bot

    def sync_calc(query):
        """ Non async wolfrmaalpha lib function """
        with open('data/apikeys.json') as f:
            api_key = json.load(f)['wolfram']

        client = wolframalpha.Client(api_key)

        # Attempt calculation
        result = client.query(query)

        if hasattr(result, 'results'):
            return next(result.results).text
        else:
            return None

    @commands.command(name='calc', aliases=['cal', 'c'])
    async def calculate(self, ctx, *, query):
        """ Calculate like, anything. """

        if not query:
            return await ctx.send('Please enter something for me to calculate!')

        # Send typing b/c this can take some time
        await ctx.trigger_typing()

        result = await self.bot.loop.run_in_executor(None, Calculator.sync_calc, query)

        if result is not None:
            await ctx.send(result)
        else:
            await ctx.send("Sorry, I couldn't calculate `{}`.".format(query))


def setup(bot):
    bot.add_cog(Calculator(bot))
