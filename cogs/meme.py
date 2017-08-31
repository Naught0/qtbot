#!/bin/env python

import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class FindMeme:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.base_uri = 'http://knowyourmeme.com{}'
        self.request_uri = 'http://knowyourmeme.com/search?context=entries&sort=relevance&q={}+category_name%3Ameme'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

    @commands.command(name='meme', aliases=['mem', 'maymay'])
    async def get_meme_info(self, ctx, *, search):
        """ Search for some dank meme information """

        request_html = await aw.aio_get_text(self.aio_session, self.request_uri.format(search.replace(' ', '+')), headers=self.headers)

        soup = BeautifulSoup(request_html, 'lxml')

        link_list = []
        for tr in soup.find_all('tr'):
            if hasattr(tr.h2, 'a'):
                link_list.append(self.base_uri.format(tr.h2.a['href']))

        if link_list:
            await ctx.send(f'{link_list[0]}')
        else:
            await ctx.send(f'Sorry, I couldn\'t find anything for `{search}`.')


def setup(bot):
    bot.add_cog(FindMeme(bot))
