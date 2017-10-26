#!/bin/env python

import discord
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class FindMeme:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.base_uri = 'http://knowyourmeme.com{}'
        self.request_uri = 'http://knowyourmeme.com/search?context=entries&sort=relevance&q={}+category_name%3Ameme'
        self.headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.101 Safari/537.36'}

    @commands.command(name='meme', aliases=['mem', 'maymay'])
    async def get_meme_info(self, ctx, *, search):
        """ Search for some dank meme information """
        f_search = search.replace(' ', '+')

        if await self.redis_client.exists(f'memecache:{f_search}'):
            link = await self.redis_client.get(f'memecache:{f_search}')

        else:
            request_html = await aw.aio_get_text(self.aio_session,
                                                 self.request_uri.format(f_search),
                                                 headers=self.headers)
            soup = BeautifulSoup(request_html, 'lxml')

            link_list = []
            for tr in soup.find_all('tr'):
                if hasattr(tr.h2, 'a'):
                    link_list.append(self.base_uri.format(tr.h2.a['href']))

            if not link_list:
                return await ctx.send(f"Sorry I wasn't able to find anything for `{search}`.")
            else:
                link = link_list[0]
                # 1 day cache time as these pages are pretty much static
                await self.redis_client.set(f'memecache:{f_search}', f'{link.encode("utf8")}', ex=86400)

        await ctx.send(f'{link}')


def setup(bot):
    bot.add_cog(FindMeme(bot))
