#!/bin/env python

import discord
import cogs.ytLib as yt
from discord.ext import commands


class YouTube():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="yt")
    async def get_youtube_video(self, *args):
        """ Returns some matching youtube videos for a query """

        if not args:
            return await self.bot.say("Go on, search something.")

        query = " ".join(args)

        # Get videos from yt API
        try:
            video_list = yt.get_video_info(query, num_results=1)
        except LookupError:
            return await self.bot.say("Sorry, couldn't find anything for `{}`.".format(query))

        # Return top hit
        return await self.bot.say("{}".format(video_list[0]["video_url"]))


def setup(bot):
    bot.add_cog(YouTube(bot))
