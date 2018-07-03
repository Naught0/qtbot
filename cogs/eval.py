import asyncio

import discord
from discord.ext import commands


class Eval:
    def __init__(self, bot):
        self.bot = bot
        self.db_conn = bot.pg_con
        self.green = discord.Color.dark_green()
        self.orange = discord.Color.dark_orange()

    @commands.command(name='eval', hidden=True)
    @commands.is_owner()
    async def shell_access(self, ctx, *, cmd):
        """ Lets me access the VPS command line via the bot """
        process = await asyncio.create_subprocess_shell(cmd, stdout=asyncio.subprocess.PIPE)
        stdout, stderr = await process.communicate()
        try:
            if stdout:
                await ctx.send(embed=discord.Embed(title=cmd,
                                                   description=f'`{cmd}`\n```{stdout.decode().strip()}```',
                                                   color=self.green))
            elif stderr:
                await ctx.send(embed=discord.Embed(title=cmd,
                                                   description=f'`{cmd}`\n```{stderr.decode().strip()}```',
                                                   color=self.green))
            else:
                await ctx.error(f'Couldn\'t grab output for ```{cmd}```.')

        except Exception as e:
            await ctx.error(f'Unable to send output ```py\n{e}```')

    @commands.command(name='git', hidden=True)
    @commands.is_owner()
    async def git_pull(self, ctx):
        """ Shortcut for .eval git pull origin master """
        cmd = self.bot.get_command('eval')
        await ctx.invoke(cmd, cmd='git pull origin master')

    @commands.group(invoke_without_command=True, name='sql', hidden=True)
    @commands.is_owner()
    async def sql_execute(self, ctx, *, query):
        """ Lets me access the postgres database via discord """
        try:
            res = await self.db_conn.execute(query)
        except Exception as e:
            return await ctx.error(f'```py\n{type(e).__name__}\n{str(e)}```')

        if not res:
            return await ctx.error(f'Sorry, `{query}` did not return anything.')

        await ctx.send(embed=discord.Embed(title=query,
                                           description=f'```sql\n{res}```',
                                           color=self.orange))

    @sql_execute.command(name='fetch')
    @commands.is_owner()
    async def sql_fetch(self, ctx, *, query):
        try:
            res = await self.db_conn.fetch(query)
        except Exception as e:
            return await ctx.error(f'```py\n{type(e).__name__}\n{str(e)}```')

        if not res:
            return await ctx.error(f'Sorry, `{query}` did not return anything.')

        em = discord.Embed(color=self.orange, title='SQL Fetch')
        for k, v in res[0].items():
            em.add_field(name=k, value=v)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Eval(bot))
