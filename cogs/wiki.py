#!/bin/env python

import discord
import wikipedia
from discord.ext import commands


class Wiki():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(pass_context=True, name="wiki", aliases=['wi'])
    async def wiki_search(self, ctx, *args):
        """ Get the closest matching Wikipedia article for query """

        query = " ".join(args)

        # Create initial embed
        em = discord.Embed()

        # No query input
        if not args:
            return await self.bot.say("Go on, search something.")

        # Search for page name
        page_name = wikipedia.search(query)[0]

        # No pages found
        if not page_name:
            return await self.bot.say("Sorry, couldn't find anything for `{}`".format(query))

        page = wikipedia.WikipediaPage(title=page_name)

        em.title = "Test"#page.title
        em.description = "Test"#"{}\n{}".format(page.url, page.summary)
        em.url = page.url
        em.type = "rich"

        return await self.bot.send_message(ctx.message.channel, embed=em)


def setup(bot):
    bot.add_cog(Wiki(bot))