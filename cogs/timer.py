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

        if int(time_in_seconds) < 3600:
            await asyncio.sleep(time_in_seconds)
        else:
            return await ctx.send('This is a test command. Please enter a time in seconds not exceeding 3600')

        await ctx.send(f':timer: {ctx.author.mention} Time is up!')


def setup(bot):
    bot.add_cog(RemindTime(bot))
