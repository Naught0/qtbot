#!/bin/env python

import discord
import asyncio
import asyncpg
from discord.ext import commands

class Eval:
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.pg_con

    @commands.command(name='eval')
    @commands.is_owner()
    async def shell_access(self, ctx, *, cmd):
        """ Lets me access the VPS command line via the bot """
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        try:
            if stdout:
                await ctx.send(f'`{cmd}`\n```{stdout.decode().strip()}```')
            elif stderr:
                await ctx.send(f'`{cmd}`\n```{stderr.decode().strip()}```')
            else:
                await ctx.send(f'`{cmd}` produced no output')

        except Exception as e:
            await ctx.send(f'Unable to send output\n```py\n{e}```')

        @commands.command(name='sql')
        @commands.is_owner()
        async def sql_execute(self, ctx, *, query):
            res = await self.db_conn.execute(query)
            await ctx.send(res)


def setup(bot):
    bot.add_cog(Eval(bot))