import csv
import random
from datetime import datetime
from typing import TypedDict, cast

import discord
from discord.ext import commands


class Tweet(TypedDict):
    id: str
    date: str
    target: str
    insult: str
    tweet: str

class Trump(commands.Cog):
    """A cog which nobody ever asked for, that fetches a random Trump tweet"""
    def __init__(self, *args, **kwargs):
        with open("data/trump_insult_tweets_2014_to_2021.csv") as f:
            self.insults = cast(tuple[Tweet], tuple(csv.DictReader(f)))

    @commands.command(name="trump", aliases=["tt"])
    async def _trump(self, ctx: commands.Context):
        """Consult the wise words of a stable genius"""
        tweet = random.choice(self.insults)
        em = discord.Embed(color=0x00ACEE)
        em.set_author(
            name="Donald J. Trump ☑️",
            icon_url="https://s3.amazonaws.com/theoatmeal-img/comics/donmojis/trump_yelling.png",
        )
        em.description = tweet["tweet"]
        em.timestamp = datetime.fromisoformat(tweet["date"])
        em.set_footer(text="via twitter", icon_url="https://i.imgur.com/DUUkDwY.png")

        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Trump(bot))
