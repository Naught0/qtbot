#!/bin/env python

import discord
import json
from discord.ext import commands
import tmdbsimple as tmdb

# TMDb info
with open("data/apikeys.json") as f:
  tmdb.API_KEY = json.load(f)["tmdb"]


class Shows:
  def __init__(self, bot):
    self.bot = bot

  @commands.command(name="show", aliases=["ss", "tv"])
  async def get_show(self, ctx, *args):
    """ Get TV show information """

    # Initialize the search
    search = tmdb.Search()

    # TMDb response & store
    response = search.tv(query=" ".join(args))
    s_result = search.results[0]

    # If no results are found
    if not s_result:
      return await ctx.send("Sorry, couldn't find that one.")

    # Get qtbot rating
    rating = float(s_result['vote_average'])
    if (rating < 7.0):
      rec = "This is not a qtbot™ recommmended show."
    else:
      rec = "This is a qtbot™ recommended show."

    # For getting poster
    base_image_uri = "https://image.tmdb.org/t/p/w185{}"

    # Get last air date / present
    if s_result["in_production"]:
      end_date = "Present"
    else:
      end_date = s_result["last_air_date"].split('-')[0]

    # Create embed
    em = discord.Embed()
    em.title = "{} ({} - {})".format(
      s_result["name"],
      s_result["first_air_date"].split('-')[0],
      end_date)
    em.description = s_result["overview"]
    em.set_thumbnail(url=base_image_uri.format(
      s_result["poster_path"]))
    em.add_field(name="Rating", value=str(rating))
    em.set_footer(text=rec)

    await ctx.send(embed=em)


def setup(bot):
  bot.add_cog(Shows(bot))
