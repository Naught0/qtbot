#!/bin/env python

import discord
import requests
from bs4 import BeautifulSoup
from discord.ext import commands


class DownDetect:
    def __init__(self, bot):
        self.bot = bot
        self.uri = "http://downforeveryoneorjustme.com/{}"

    @commands.command(name="isup", aliases=["dd"])
    async def down_detector(self, ctx, check_url):
        """ Check whether a website is down or up """

        request_html = requests.get(self.uri.format(check_url)).text

        # Get soupy
        soup = BeautifulSoup(request_html, "html.parser")

        # Ugly but ensures that a website with "not"
        # Is not erroneously detected
        isup_result = str(soup.find("p")).split(">")[1].strip().split("<")[0]

        if "not" in isup_result:
            await ctx.send("`{}` Looks down from here.".format(check_url))
        else:
            await ctx.send("`{}` Looks up from here.".format(check_url))


def setup(bot):
    bot.add_cog(DownDetect(bot))
