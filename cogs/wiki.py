#!/bin/env python

import discord
import wikipedia
import textwrap
from discord.ext import commands


class Wiki:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="wiki", aliases=['wi'])
    async def wiki_search(self, ctx, *, query=None):
        """ Get the closest matching Wikipedia article for query """

        # Create initial embed
        em = discord.Embed()

        # Neat wiki icon
        em.set_thumbnail(
            url="https://lh5.ggpht.com/1Erjb8gyF0RCc9uhnlfUdbU603IgMm-G-Y3aJuFcfQpno0N4HQIVkTZERCTo65Iz2II=w300")

        # No query input
        # Returns random article
        if not query:
            em.title = wikipedia.random(pages=1)
            page = wikipedia.page(title=em.title)
            em.description = textwrap.shorten(
                page.summary, width=240, placeholder="...")
            em.url = page.url
            return await ctx.send(embed=em)

        # Search for page name
        # I modified the library to return the first result if there is a
        # disambiguation exception
        page_title = wikipedia.search(query)

        # No pages found
        if not page_title:
            return await ctx.send("Sorry, couldn't find anything for `{}`".format(query))

        # Page object
        page = wikipedia.page(title=page_title)

        # Create embed
        em.title = page.title
        em.description = textwrap.shorten(
            page.summary, width=240, placeholder="...")
        em.url = page.url

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))
