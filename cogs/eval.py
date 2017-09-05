#!/bin/env python

import discord
import asyncio
from discord.ext import commands

class Eval:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='eval')
    @commands.is_owner()
    async def shell_access(self, ctx, *, cmd):
        """ Lets me access the VPS command line via the bot """
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        try:
            if stdout:
                await ctx.send(f'`{cmd}`\n```{stdout.decode().strip()}```')
            else:
                await ctx.send(f'`{cmd}` produced no output')
        except Exception as e:
            await ctx.send(f'Unable to send output\n```py\n{e}```')


def setup(bot):
    bot.add_cog(Eval(bot))