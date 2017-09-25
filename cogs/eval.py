#!/bin/env python

import discord
import asyncio
from pprint import pformat
from discord.ext import commands

class Eval:
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.pg_con

    @commands.command(name='eval', hidden=True)
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

    @commands.group(invoke_without_command=True, name='sql', hidden=True)
    @commands.is_owner()
    async def sql_execute(self, ctx, *, query):
        """ Lets me access the postgres database via discord """
        try:
            res = await self.db_conn.execute(query)
        except Exception as e:
            return await ctx.send(f'```py\n{type(e).__name__}\n{str(e)}```')

        await ctx.send(f'```sql\n{res}```')

    @sql_execute.command(name='fetch')
    async def sql_fetch(self, ctx, *, query):
        try:
            res = await self.db_conn.fetch(query)
        except Exception as e:
            return await ctx.send(f'```py\n{type(e).__name__}\n{str(e)}```')

        record_dict = {}
        for k, v in res[0].items():
            record_dict[k] = v

        await ctx.send(pformat(record_dict))


def setup(bot):
    bot.add_cog(Eval(bot))