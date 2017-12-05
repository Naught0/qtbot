import discord
import random
import json
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class RNG:
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.fact_url = 'http://www.unkno.com/'
        self.react_url = 'http://api.chew.pro/trbmb'

    @commands.command(aliases=['facts'])
    async def fact(self, ctx):
        """ Get a random fun fact (potentially NSFW) """
        html = await aw.aio_get_text(self.session, self.fact_url)
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

    @commands.command(aliases=['re'])
    async def react(self, ctx):
        """ Have qtbot react with something inane """
        # Have to get text because it has the wrong content-type
        resp = await aw.aio_get_text(self.session, self.react_url)
        reaction = json.loads(resp)[0]
        await ctx.send(f'{reaction}!')


def setup(bot):
    bot.add_cog(RNG(bot))
