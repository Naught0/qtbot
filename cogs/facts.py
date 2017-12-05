import discord
import random
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class Facts:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.url = 'http://www.unkno.com/'

    @commands.command(aliases=['facts'])
    async def fact(self, ctx):
        """ Get a random fun fact (potentially NSFW) """
        html = await aw.aio_get_text(self.session, self.url)
        soup = BeautifulSoup(html, 'lxml')

        try:
            fun_fact = soup.find('div', id='content').text.strip()
        except AttributeError:
            return await ctx.send(random.choice(['Sorry, I get nervous in front of crowds',
                                                 "Oh god, I'm blanking",
                                                 "Just a second, I'll think of something...",
                                                 'This is no time for fun or facts.']))

        # Create embed
        em = discord.Embed(description=fun_fact)
        em.set_thumbnail(url='https://i.imgur.com/c36rUx9.png')

        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Facts(bot))
