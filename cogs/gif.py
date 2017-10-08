import discord
from utils import giphy_wrapper as gwrap
from discord.ext import commands


class Giphy:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session


    @commands.command(name='gif', aliases=['jif', 'jiff'])
    async def giphy(self, ctx, *, query=None):
        """ returns a random gif matching a query """
        gif_result = await gwrap.rand_search(self.aio_session, query=query)

        if gif_result:
            await ctx.send(gif_result['url'])
        else:
            await ctx.send(f"Sorry, I couldn't find anything for `{query}`.")

    @commands.command(aliases=['ty', 'thank'])
    @commands.cooldown()
    async def thanks(self, ctx):
        """ Thank your overlord, qtbot """
        gif_result = await gwrap.rand_search(self.aio_session, query='blushing')

        await ctx.send(gif_result['fixed_width_downsampled_url'])

def setup(bot):
    bot.add_cog(Giphy(bot))
