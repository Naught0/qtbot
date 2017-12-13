import discord 
import json
from discord.ext import commands
from datetime import datetime 

from utils import aiohttp_wrap as aw 


class Game:
    """ Cog which allows fetching of video game information """
    IG_URL = 'https://api-2445582011268.apicast.io/{}/'
    IG_ICON_URL = 'https://www.igdb.com/favicon-196x196.png'
    with open('data/apikeys.json') as f:
        KEY = json.load(f)['igdb']

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
    
    @commands.command(aliases=['games'])
    async def game(self, ctx, *, query: str):
        """ Search for some information about a game """
        url = self.IG_URL.format('games')
        headers = {'user-key': self.KEY}
        params = {'search': query, 
                  'fields': 'name,summary,first_release_date,aggregated_rating,cover'}
        
        resp = (await aw.aio_get_json(self.session, url, headers=headers, params=params))[0]

        return print(resp.keys())

        # Create embed
        em = discord.Embed(timestamp=datetime.fromtimestamp(resp['first_release_date']//1000), 
                           url=resp['url'],
                           color=discord.Color.green())
        em.description = resp['summary']
        em.set_author(name=resp['name'], icon_url=self.IG_ICON_URL)
        em.set_thumbnail(url=resp['cover']['url'])
        em.add_field(name='Rating', value=resp['aggregated_rating'])
        em.set_footer(text='First released')

        await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(Game(bot))
