import discord
import giphypop
from discord.ext import commands


class Giphy:
    def __init__(self, bot):
        self.bot = bot

    def sync_giphy(query=None):
        """ Non async giphy library function """
        giphy_instance = giphypop.Giphy()

        if query is None:
            return giphy_instance.random_gif()

        gif = giphy_instance.random_gif(query)

        if gif:
            return gif

        return gif

    @commands.command(name='gif', aliases=['jif', 'jiff'])
    async def giphy(self, ctx, *, query=None):
        """ returns a random gif matching a query """
        gif_result = await self.bot.loop.run_in_executor(None, Giphy.sync_giphy, query)

        if gif_result:
            await ctx.send(gif_result.media_url)
        else:
            await ctx.send("Sorry, I couldn't find anything for `{}`.".format(query))

    # Thanks qtbot!
    @commands.command(aliases=['ty', 'thank'])
    async def thanks(self, ctx):
        """ Thank your overlord, qtbot """
        gif_result = await self.bot.loop.run_in_executor(None, Giphy.sync_giphy, 'blushing')

        await ctx.send(gif_result.fixed_width.downsampled.url)


def setup(bot):
    bot.add_cog(Giphy(bot))
