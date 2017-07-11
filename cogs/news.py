#!/bin/evn python
import discord
import json
import requests
import requests_cache
from discord.ext import commands


with open("data/apikeys.json") as f:
    news_api_key = json.load(f)["news"]

uri = "https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey={}"


class News():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="news")
    async def get_news(self, num_results=3):
        """ Get the top x articles from Google News (powered by https://newsapi.org/) """

        if num_results < 1 or num_results > 5:
            return await self.bot.say("Sorry, please choose a number of results between 1 and 5 inclusive.")

        # Call to API
        raw_result = requests.get(uri.format(news_api_key)).json()

        article_list = []

        for x in range(num_results):
            article_list.append("".join(["`", raw_result["articles"][x]["title"], "`"]))
            article_list.append("".join(["<", raw_result["articles"][x]["url"], ">"]))

        # Found a better way
        return await self.bot.say("\n".join(article_list))


def setup(bot):
    bot.add_cog(News(bot))
