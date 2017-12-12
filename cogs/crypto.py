import discord
import datetime
from discord.ext import commands
from utils import aiohttp_wrap as aw


class Crypto:
    """ Allows users to track bitcoin and other currencies """
    URL_BTC = 'https://api.coinmarketcap.com/v1/ticker/bitcoin' 
    BTC_LOGO_URL = 'https://en.bitcoin.it/w/images/en/2/29/BC_Logo_.png'
    
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session

    @commands.command(aliases=['btc'])
    async def bitcoin(self, ctx):
        """ Get current information regarding the value of bitcoin """
        resp = (await aw.aio_get_json(self.session, self.URL_BTC))[0]

        # Create a neat embed with the information
        em = discord.Embed(color=discord.Color.gold())
        em.set_author(name='Bitcoin', icon_url=self.BTC_LOGO_URL)
        em.add_field(name='Price USD', value=f"${resp['price_usd']}")

        # Add some arrows here, so we need some logic
        change_1h = r['percent_change_1h']
        change_1h_str = f":arrow_up: {change_1h}" if '-' in change_1h else f":arrow_down: {change_1h}"
        em.add_field(name='Percent Change 1h', value=change_1h_str)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Crypto(bot))
