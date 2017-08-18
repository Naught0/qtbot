#!/bin/env python

import discord
from discord.ext import commands


class Admin:
    def __init__(self, bot):
        self.bot = bot

    async def on_member_join(self, ctx):
        await ctx.send("Welcome to the server! For a complete list of commands, type `.help`.")

    @commands.command()
    @commands.is_owner()
    async def load(self, ctx, extension_name: str):
        """ Loads an extension """
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            return await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
        await ctx.send("Cog `{}` loaded successfully.".format(extension_name))


    @commands.command()
    @commands.is_owner()
    async def unload(self, ctx, extension_name: str):
        """ Unloads an extension. """
        self.bot.unload_extension(extension_name)
        await ctx.send("Cog `{}` has been unloaded.".format(extension_name))


    @commands.command(aliases="r")
    @commands.is_owner()
    async def reload(self, ctx, extension_name: str):
        """ Reloads an extension """
        self.bot.unload_extension(extension_name)
        self.bot.load_extension(extension_name)
        await ctx.send("Cog `{}` has been reloaded.".format(extension_name))


def setup(bot):
    bot.add_cog(Admin(bot))