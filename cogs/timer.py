#!/bin/env python

import asyncio
import discord
import json
from discord.ext import commands


class Timer:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='time')
    async def create_remind(self, ctx, time):
        """ Create a timer in seconds """
        sleep = int(time)

        if sleep < 7200:
            await ctx.send(f'Timer set for `{sleep}` seconds.')
            await asyncio.sleep(sleep)
            await ctx.send(f':timer: {ctx.author.mention} Time is up!')

        else:
            return await ctx.send('This is a test command. Please enter a time in seconds not exceeding 7200.')


def setup(bot):
    bot.add_cog(Timer(bot))
