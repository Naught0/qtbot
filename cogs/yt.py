#!/bin/env python

import discord
from utils import yt_funcs as yt
from discord.ext import commands


class YouTube:
    def __init__(self, bot):
        self.bot = bot

    def sync_get_youtube_video(query):
        """ Sync youtube function (lib uses requests) """
        return yt.get_video_info(query, num_results=1)

    @commands.command(name='yt')
    async def get_youtube_video(self, ctx, *, query):
        """ Returns some matching youtube videos for a query """

        if not query:
            return await ctx.send('Go on, search something.')

        # Executor for sync function
        video_list = await self.bot.loop.run_in_executor(None, YouTube.sync_get_youtube_video, query)

        if not video_list:
            return await ctx.say("Sorry, couldn't find anything for `{}`".format(query))

        # Return top hit
        await ctx.send('{}'.format(video_list[0]['video_url']))


def setup(bot):
    bot.add_cog(YouTube(bot))
