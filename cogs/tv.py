#!/bin/env python

import discord
import json
from discord.ext import commands
import tmdbsimple as tmdb

# TMDb info
with open("data/apikeys.json") as f:
    tmdb.API_KEY = json.load(f)["tmdb"]


class Shows():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(name="show", aliases=["ss", "tv"])
    async def get_show(self, *args):
        """ Get TV show information """
        search = tmdb.Search()

        response = search.tv(query=" ".join(args))

        s_results = search.results

        if not s_results:
            return await self.bot.say("Sorry, couldn't find that one.")

        rating = float(s_results[0]['vote_average'])
        if (rating < 7.0):
            rec = "This is not a qtbot™ recommmended show."
        else:
            rec = "This is a qtbot™ recommended show."

        # For getting poster
        base_image_uri = "https://image.tmdb.org/t/p/w185{}"

        # Create embed
        em = discord.Embed()
        em.title = "{} ({})".format(
            s_results[0]["name"], s_results[0]["first_air_date"].split('-')[0])
        em.description = s_results[0]["overview"]
        em.set_thumbnail(url=base_image_uri.format(
            s_results[0]["poster_path"]))
        em.add_field(name="Rating", value=str(rating))
        em.set_footer(text=rec)

        return await self.bot.say(embed=em)


def setup(bot):
    bot.add_cog(Shows(bot))
