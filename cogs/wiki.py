#!/bin/env python

import discord
from discord.ext import commands
from utils import aiohttp_wrap as aw


class Wiki:
    def __init__(self, bot):
        self.bot = bot
        self.search_uri = 'http://en.wikipedia.org/w/api.php?action=opensearch&format=json&search={}'
        self.random_uri = 'https://en.wikipedia.org/w/api.php?action=query&list=random&format=json&rnnamespace=0&rnlimit=1'
        self.headers = {'user-agent': 'qtbot/1.0 - A friendly discord bot (https://github.com/Naught0/qtbot)'}
        self.aio_session = bot.aio_session

    async def get_wiki_data(self, query=None):
        """ Wrapper that returns wikipedia data in an easily digestible format """

        # Determine whether we want a random article
        if not query:
            formatted_query = await aw.aio_get_json(self.aio_session, self.random_uri, headers=self.headers)['query']['random'][0]['title'].replace(' ', '+')

        # Spaces -> +
        formatted_query = query.replace(' ', '+')

        # Get wiki page
        resp = await aw.aio_get_json(self.aio_session, self.search_uri.format(formatted_query), headers=self.headers)

        # No result found
        if not resp[1]:
            return None

        return {'title': resp[1][0], 'description': resp[2][0], 'link': resp[3][0]}

    @commands.command(name='wiki', aliases=['wi'])
    async def wiki_seearch(self, ctx, *, query=None):
        """ Get the closest matching Wikipedia article for a given query """

        wiki_info = Wiki.get_wiki_data(query)

        if not wiki_info:
            return await ctx.send(f'Sorry, I couldn\'t find anything for {query}')

        # Create embed
        em = discord.Embed()
        em.title = wiki_info['title']
        em.description = wiki_info['description']
        em.url = wiki_info['link']
        em.set_thumbnail(url='https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300')

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
