#!/bin/env python

import discord
from utils import aiohttp_wrap as aw
from bs4 import BeautifulSoup
from discord.ext import commands


class DownDetect:
    def __init__(self, bot):
        self.bot = bot
        self.uri = 'http://downforeveryoneorjustme.com/{}'
        self.aio_session = bot.aio_session

    @commands.command(name='isup', aliases=['dd'])
    @commands.cooldown(rate=1, per=2.0, type=commands.BucketType.user)
    async def down_detector(self, ctx, check_url):
        """ Check whether a website is down or up """

        request_html = await aw.aio_get_text(self.uri.format(check_url))

        # Get soupy
        soup = BeautifulSoup(request_html, 'html.parser')

        # Ugly but ensures that a website with 'not' in the url
        # Is not erroneously detected
        isup_result = str(soup.find('p')).split('>')[1].strip().split('<')[0]

        if 'not' in isup_result:
            await ctx.send('`{}` Looks down from here.'.format(check_url))
        else:
            await ctx.send('`{}` Looks up from here.'.format(check_url))


def setup(bot):
    bot.add_cog(DownDetect(bot))
