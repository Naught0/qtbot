import discord
import giphypop
from discord.ext import commands


class Giphy():
    def __init__(self, bot):
        self.bot = bot

    # Giphy
    @commands.bot.command(aliases=['gif', 'jif', 'jiff'])
    async def giphy(self, *args):
        """ returns a random gif matching a query """
        q = " ".join(args)
        gif = giphypop.Giphy()
        result = gif.random_gif(q)

        try:
            await self.bot.say(result.media_url)
        except:
            await self.bot.say("Sorry, couldn't find anything for `{}`".format(q))
        return

    # Thanks qtbot!
    @commands.bot.command(aliases=['ty'])
    async def thanks(self):
        """ Thank your overlord, qtbot """
        g = giphypop.Giphy()
        gif = g.random_gif("blushing")
        formGif = gif.fixed_width.downsampled.url

        return await self.bot.say(formGif)


def setup(bot):
    bot.add_cog(Giphy(bot))
