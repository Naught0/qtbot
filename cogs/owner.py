import discord
from discord.ext import commands


class Owner(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # async def on_member_join(self, ctx):
    #     await ctx.send('Welcome to the server! For a complete list of commands, type `.help`.')

    @commands.command(aliases=['l'], hidden=True)
    @commands.is_owner()
    async def load(self, ctx, extension_name: str):
        """ Loads an extension """
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            return await ctx.send(f'```py\n{type(e).__name__}: {str(e)}\n```')

        await ctx.success(f'Cog `{extension_name}` loaded successfully.')

    @commands.command(aliases=['unl'], hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, extension_name: str):
        """ Unloads an extension. """
        self.bot.unload_extension(extension_name)
        await ctx.success(f'Cog `{extension_name}` has been unloaded.')

    @commands.command(aliases=['r'], hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension_name: str):
        """ Reloads an extension """
        self.bot.reload_extension(extension_name)
        await ctx.success(f'Cog `{extension_name}` has been reloaded.')

    @commands.command(name='reload_all', aliases=['ra'], hidden=True)
    @commands.is_owner()
    async def reload_all(self, ctx):
        """ Reloads all extensions """
        # Gets cog list and removes admin cog (can't reload without it)
        ext_list = []
        for extension in self.bot.startup_extensions:
            ext_list.append(f'cogs.{extension}')
        ext_list.remove(ext_list.index('cogs.owner'))

        # Reloads all cogs
        for extension in ext_list:
            self.bot.reload_extension(extension)
        await ctx.success(f'Reloaded `{len(self.bot.startup_extensions)}` extensions.')


def setup(bot):
    bot.add_cog(Owner(bot))
