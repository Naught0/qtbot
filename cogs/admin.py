#!/bin/env python

import discord
from datetime import datetime
from discord.ext import commands


class Admin:
    def __init__(self, bot):
        self.bot = bot

    # async def on_member_join(self, ctx):
    #     await ctx.send('Welcome to the server! For a complete list of commands, type `.help`.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name: str):
        """ Loads an extension """
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            return await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')
        await ctx.send('Cog `{}` loaded successfully.'.format(extension_name))

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name: str):
        """ Unloads an extension. """
        self.bot.unload_extension(extension_name)
        await ctx.send('Cog `{}` has been unloaded.'.format(extension_name))

    @commands.command(name='reload', aliases='r', hidden=True)
    @commands.is_owner()
    async def _reload(self, ctx, extension_name: str):
        """ Reloads an extension """
        try:
            self.bot.unload_extension(extension_name)
            self.bot.load_extension(extension_name)
        except Exception as e:
            return await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')
        await ctx.send(f'Cog `{extension_name}` has been reloaded.')

    @commands.command(name='reload_all', aliases=['ra'], hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx):
        """ Reloads all extensions """

        # Gets cog list and pops admin cog (can't reload without it)
        ext_list = []
        for extension in self.bot.startup_extensions:
            ext_list.append(extension)
        ext_list.pop(ext_list.index('cogs.admin'))

        # Reloads all cogs
        for extension in ext_list:
            try:
                self.bot.unload_extension(extension)
                self.bot.load_extension(extension)
            except Exception as e:
                return await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')

        await ctx.send('All cogs have been reloaded.')

    @commands.command(name='clean', aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    async def clean_bot_messages(self, ctx, num_msg: int):
        """ Remove a given number of bot messages """

        if num_msg > 100:
            return await ctx.send('Sorry, number of messages to be deleted must not exceed 100.')

        # Check so that only bot msgs are removed
        def check(message):
            return message.author.id == self.bot.user.id

        try:
            await ctx.channel.purge(check=check, limit=num_msg)
        except Exception as e:
            await ctx.send(f'Failed to delete messages.\n ```py\n{e}```')

    @commands.command(aliases=['up'])
    async def uptime(self, ctx):
        """Get current bot uptime."""
        current_time = datetime.now()
        current_time_str = current_time.strftime('%B %d %H:%M:%S')
        await ctx.send(f'Initialized `{self.bot.start_time_str}`\nCurrent Time: `{current_time_str}`\nUptime: '\
                       f'`{str(current_time - self.bot.start_time).split(".")[0]}`')

def setup(bot):
    bot.add_cog(Admin(bot))
