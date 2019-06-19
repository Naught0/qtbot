import discord
from utils import aiohttp_wrap as aw
from bs4 import BeautifulSoup
from discord.ext import commands


class DownDetect(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.uri = 'http://downforeveryoneorjustme.com/{}'
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client

    @commands.command(name='isup', aliases=['dd'])
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def down_detector(self, ctx, check_url):
        """ Check whether a website is down or up """

        # Recent result found in cache (< 5 minutes)
        if await self.redis_client.exists(f'isup:{check_url}'):
            if await self.redis_client.get(f'isup:{check_url}'):
                return await ctx.send(f'`{check_url}` Looks up from here.')
            else:
                return await ctx.send(f'`{check_url}` Looks down from here.')

        # Recent result not cached
        else:
            request_html = await aw.aio_get_text(self.aio_session, self.uri.format(check_url))

            # Get soupy
            soup = BeautifulSoup(request_html, 'html.parser')

            # Ugly but ensures that a website with 'not' in the url
            # Is not erroneously detected
            isup_result = str(soup.find('p')).split('>')[1].strip().split('<')[0]

            if 'not' in isup_result:
                await ctx.send(f'`{check_url}` Looks down from here.')
                await self.redis_client.set(f'isup:{check_url}', False, ex=300)
            else:
                await ctx.send(f'`{check_url}` Looks up from here.')
                await self.redis_client.set(f'isup:{check_url}', True, ex=300)


def setup(bot):
    bot.add_cog(DownDetect(bot))
