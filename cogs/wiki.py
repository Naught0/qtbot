#!/bin/env python

import discord
import wikipedia
import textwrap
from discord.ext import commands

""" TODO: Modify wikipedia library to return first article entry when a
disambiguation exception ocurrs """


class Wiki:
    def __init__(self, bot):
        self.bot = bot

    def sync_wiki_search(query=None):
        """ Non async wiki search """
        if not query:
            article_title = wikipedia.random(pages=1)
            article_obj = wikipedia.page(title=article_title)
            return {'title': article_title, 'description': texwrap.shorten(article_obj.summary, width=240, placeholder='...'), 'url': article_obj.url}

        article_title = wikipedia.search(query)
        if not article_title:
            return None
        else:
            article_obj = wikipedia.page(title=article_title)
            return {'title': article_title, 'description': texwrap.shorten(article_obj.summary, width=240, placeholder='...'), 'url': article_obj.url}

    @commands.command(name='wiki', aliases=['wi'])
    async def wiki_search(self, ctx, *, query=None):
        """ Get the closest matching Wikipedia article for query """

        # Run sync function
        wiki_dict = await self.bot.loop.run_in_executor(None, Wiki.sync_wiki_search, query)

        # No pages found
        if not wiki_dict:
            return await ctx.send("Sorry, couldn't find anything for `{}`".format(query))

        # Create embed
        em = discord.Embed()
        em.title = wiki_dict['title']
        em.description = wiki_dict['description']
        em.url = wiki_dict['url']
        em.set_thumbnail(
            url='https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300')

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
