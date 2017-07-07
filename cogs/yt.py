#!/bin/env python

import discord
import cogs.ytLib as yt
from discord.ext import commands


class YouTube():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="youtube", aliases=["yt"])
    async def get_youtube_video(self, *args):
        """ Returns some matching youtube videos for a query """

        query = " ".join(args)

        # Get videos from yt API
        try:
            video_list = yt.get_video_info(query, num_results=3)
        except LookupError:
            return await self.bot.say("Sorry, couldn't find anything for `{}`.".format(query))

        # Good God I'm sorry for this
        format_str = "**{}**\n<{}>\n```{}```\n**See Also:**\n```{}:\n{}\n\n{}:\n{}```".format(
            video_list[0]["title"], video_list[0]["video_url"], video_list[0]["description"], video_list[1]["title"], video_list[1]["video_url"], video_list[2]["title"], video_list[2]["video_url"])

        return await self.bot.say(format_str)


def setup(bot):
    bot.add_cog(YouTube(bot))
