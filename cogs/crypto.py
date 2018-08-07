import datetime
import json
import discord
from discord.ext import commands
from utils import aiohttp_wrap as aw


class Crypto:
    """ Allows users to track bitcoin and other currencies (eventually) """
    URL_BTC = 'https://api.coinmarketcap.com/v1/ticker/bitcoin' 
    BTC_LOGO_URL = 'https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png'
    
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.redis = bot.redis_client

    @commands.command(aliases=['btc', 'buttcoin'])
    async def bitcoin(self, ctx):
        """ Get current information regarding the value of bitcoin """

        # Check the cache for this information
        if await self.redis.exists('btc'):
            resp = json.loads(await self.redis.get('btc'))

        # If not found, cache for 5 minutes
        else:
            resp = (await aw.aio_get_json(self.session, self.URL_BTC))[0]
            await self.redis.set('btc', json.dumps(resp), ex=5*60)

        # Create a neat embed with the information
        em = discord.Embed(color=0xF7931A)
        em.set_author(name='Bitcoin', icon_url=self.BTC_LOGO_URL)
        em.add_field(name='Price USD', value=f"${float(resp['price_usd']):,.2f}", inline=False)
        em.set_footer(text='Last updated')
        em.timestamp = datetime.datetime.fromtimestamp(int(resp['last_updated']))

        # Hourly trend
        change_1h = resp['percent_change_1h']
        change_1h_str = f":arrow_up: {change_1h}%" if '-' not in change_1h else f":arrow_down: {change_1h}%"
        em.add_field(name='Hourly trend', value=change_1h_str)

        # Daily trend
        change_24h = resp['percent_change_24h']
        change_24h_str = f":arrow_up: {change_24h}%" if '-' not in change_24h else f":arrow_down: {change_24h}%"
        em.add_field(name='Daily trend', value=change_24h_str)

        # Weekly trend
        change_7d = resp['percent_change_7d']
        change_7d_str = f":arrow_up: {change_7d}%" if '-' not in change_7d else f":arrow_down: {change_7d}%"
        em.add_field(name='Weekly trend', value=change_7d_str)

        # Ticker graph
        em.set_image(url='https://s2.coinmarketcap.com/generated/sparklines/web/7d/usd/1.png')

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Crypto(bot))
