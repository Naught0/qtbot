#!/bin/evn python
import discord
import json
import requests
import requests_cache
from discord.ext import commands


with open("data/apikeys.json") as f:
    news_api_key = json.load(f)["news"]

uri = "https://newsapi.org/v1/articles?source=google-news&sortBy={}&apiKey={}"


class News():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="news")
    async def get_news(self, sort_by="top"):
        """ Get top, latest, or popular news from Google, powered by https://newsapi.org/ """

        # All allowed
        sorting_list = ["top", "latest", "popular"]

        if not sort_by.lower() in sorting_list:
            return await self.bot.say("Sorry, please chose `.news` followed by `top` `latest` `popular` or nothing at all to get news.")

        raw_result = requests.get(uri.format(sort_by, news_api_key)).json()

        return await self.bot.say("`{}`\n<{}>\n`{}`\n<{}>\n`{}`\n<{}>\n`{}`\n<{}>\n`{}`\n<{}>".format(raw_result["articles"][0]["title"], raw_result["articles"][0]["url"], raw_result["articles"][1]["title"], raw_result["articles"][1]["url"], raw_result["articles"][2]["title"], raw_result["articles"][2]["url"], raw_result["articles"][3]["title"], raw_result["articles"][3]["url"], raw_result["articles"][4]["title"], raw_result["articles"][4]["url"]))


def setup(bot):
    bot.add_cog(News(bot))
