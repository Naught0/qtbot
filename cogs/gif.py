import discord, giphypop
from discord.ext import commands

class Giphy():
    def __init__(self, bot):
        self.bot = bot
        
    # Giphy 
    @commands.bot.command(aliases = ['gif', 'jif', 'jiff'])
    async def giphy(self, *args):
        """ returns a random gif matching a query """
        self.q = " ".join(args)
        self.gif = giphypop.Giphy()
        self.result = self.gif.random_gif(self.q)

        try:
            await self.bot.say(self.result.media_url)
        except:
            await self.bot.say("Sorry, couldn't find anything for `{}`".format(self.q))
        return
        
    # Thanks qtbot!
    @commands.bot.command(aliases = ['ty'])
    async def thanks(self):
        """ Thank your overlord, qtbot """
        self.g = giphypop.Giphy()
        self.gif = self.g.random_gif("blushing")
        self.formGif = self.gif.fixed_width.downsampled.url

        return await self.bot.say(self.formGif)

def setup(bot):
    bot.add_cog(Giphy(bot))