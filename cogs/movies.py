import discord
import json
from discord.ext import commands
import tmdbsimple as tmdb

# TMDb info
with open("data/apikeys.json") as f:
    api_keys = json.load(f)

tmdb.API_KEY = api_keys["tmdb"]


class Movies():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(aliases=['movie', 'mov'])
    async def getMovie(self, *args):
        """ Get basic info about a movie """
        search = tmdb.Search()

        response = search.movie(query=" ".join(args))

        s_results = search.results

        if not s_results:
            return await self.bot.say("Sorry, couldn't find that one.")

        rating = float(s_results[0]['vote_average'])
        if (rating < 7.0):
            rec = "This is not a qtbot™ recommmended film."
        else:
            rec = "This is a qtbot™ recommended film."

        return await self.bot.say("Title: `{}`\nYear: `{}`\nPlot: `{}`\nTMDb rating: `{}`\n{}".format(s_results[0]['title'], (s_results[0]['release_date']).split('-')[0], s_results[0]['overview'], rating, rec))


def setup(bot):
    bot.add_cog(Movies(bot))
