import discord 
from discord.ext import commands
from datetime import datetime 

from utils import aiohttp_wrap as aw 


class Game:
    """ Cog which allows fetching of video game information """
    IG_URL = 'https://api-2445582011268.apicast.io/{}/'
    with open('data/apikeys.json') as f:
        KEY = json.load(f)['pgdb']

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
    
    @commands.comand(aliases=['games'])
    async def game(self, ctx, *, query: str):
        """ Search for some information about a game """
        url = self.IG_URL.format('games')
        headers = {'user-key': self.KEY}
        params = {'search': query, 
                  'fields': 'name,summary,first_release_date,aggregated_rating,cover'}
        
        resp = await aw.aio_get_json(self.session, url, headers=headers, params=params)

        await ctx.send(f'{resp}'[:500])

def setup(bot):
    bot.add_cog(Game(bot))
