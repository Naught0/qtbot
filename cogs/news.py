#!/bin/evn python
import discord
import json
import requests
import requests_cache
from discord.ext import commands


class News:
    def __init__(self, bot):
        self.bot = bot
        with open("data/apikeys.json") as f:
            self.api_key = json.load(f)["news"]
        self.uri = "https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey={}"

    @commands.command(name="news")
    async def get_news(self, ctx, num_results=3):
        """ Get the top 1 - 5 (default 3) articles from Google News (powered by https://newsapi.org/) """

        # More than 5 is very spammy
        if num_results < 1 or num_results > 5:
            return await ctx.send("Sorry, please choose a number of results between 1 and 5 inclusive.")

        # Cache those calls
        requests_cache.install_cache(expire_after=1800)

        # Call to API
        raw_result = requests.get(self.uri.format(self.api_key)).json()

        article_list = []

        for x in range(num_results):
            article_list.append(
                "".join(["`", raw_result["articles"][x]["title"], "`"]))
            article_list.append(
                "".join(["<", raw_result["articles"][x]["url"], ">"]))

        # Found a better way
        await ctx.send("\n".join(article_list))


def setup(bot):
    bot.add_cog(News(bot))
