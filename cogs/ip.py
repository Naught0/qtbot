import discord
from discord.ext import commands
from utils import aiohttp_wrap as aw
import time

class IPLookup:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.api_uri = 'http://ip-api.com/json/{}'

    @commands.command(aliases=['ip'])
    async def iplookup(self, ctx, *, query: str):
        """ Get information about an IP or website """
        res = await aw.aio_get_json(self.aio_session, self.api_uri.format(query))

        # Check whether successful
        if not res or res['status'] == 'fail':
            return await ctx.send(f"Sorry, I couldn't find any data on `{query}`.")

        em = discord.Embed(title=res['org'], color=discord.Color.dark_magenta())
        em.add_field(name='Location', value=f"{res['city']}, {res['regionName']}, {res['country']}", inline=False)
        em.add_field(name='Coordinates', value=f"({res['lat']:.3f}, {res['lon']:.3f})")
        em.add_field(name='ISP', value=res['as'])
        em.set_thumbnail(url='https://u.teknik.io/ySnYY.png')
        em.set_image(
            url=f"https://maps.googleapis.com/maps/api/staticmap?center={res['lat']:.3f},{res['lon']:.3f}&zoom=13&scale=false&size=255x255&maptype=roadmap&format=png")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(IPLookup(bot))
