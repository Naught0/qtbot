#!/bin/env python

import discord
import asyncio
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

        if not res:
            return await ctx.send(f'Sorry, `{query}` did not return anything.')

        await ctx.send(f'```sql\n{res}```')

    @sql_execute.command(name='fetch')
    async def sql_fetch(self, ctx, *, query):
        try:
            res = await self.db_conn.fetch(query)
        except Exception as e:
            return await ctx.send(f'```py\n{type(e).__name__}\n{str(e)}```')

        if not res:
            return await ctx.send(f'Sorry, `{query}` did not return anything.')

        em = discord.Embed(color=discord.Color.dark_orange(), title='SQL Fetch')
        for k, v in res[0].items():
            em.add_field(name=k, value=v)

        await ctx.send(embed=em)

    @commands.command(name='em', hidden=True)
    @commands.is_owner()
    async def msg_to_embed(self, ctx, *args):
        """ Convert message to embed """
        em = discord.Embed(title=args[0])
        args.pop(0)
        i = 0

        for x in args:
            em.add_field(name=f'Field {i}:', value=x)
            i += 1

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Eval(bot))