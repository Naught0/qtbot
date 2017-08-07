import discord
import giphypop
from discord.ext import commands


class Giphy:
    def __init__(self, bot):
        self.bot = bot

    # Giphy
    @commands.command(aliases=['gif', 'jif', 'jiff'])
    async def giphy(self, ctx, *args):
        """ returns a random gif matching a query """
        q = " ".join(args)
        gif = giphypop.Giphy()
        result = gif.random_gif(q)

        try:
            await ctx.send(result.media_url)
        except:
            await ctx.send("Sorry, couldn't find anything for `{}`".format(q))

    # Thanks qtbot!
    @commands.command(aliases=['ty'])
    async def thanks(ctx, self):
        """ Thank your overlord, qtbot """
        g = giphypop.Giphy()
        gif = g.random_gif("blushing")
        formGif = gif.fixed_width.downsampled.url

        await ctx.send(formGif)


def setup(bot):
    bot.add_cog(Giphy(bot))
