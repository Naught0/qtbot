#!/bin/env python

import asyncio
import discord
import json
from discord.ext import commands


class RemindTime:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='remindme')
    async def create_remind(self, ctx, time_in_seconds):
        """ Create a reminder to do something """
        sleep = int(time_in_seconds)

        if sleep < 3600:
            await ctx.send(f'Timer set for `{sleep}` seconds.')
            await asyncio.sleep(sleep)
            await ctx.send(f':timer: {ctx.author.mention} Time is up!')

        else:
            return await ctx.send('This is a test command. Please enter a time in seconds not exceeding 3600.')


def setup(bot):
    bot.add_cog(RemindTime(bot))
