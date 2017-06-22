import discord
import json
from discord.ext import commands
import tmdbsimple as tmdb

# TMDb info
with open("data/apikeys.json", "r") as f:
    apiKeys = json.load(f)
f.close()

tmdb.API_KEY = apiKeys["tmdb"]


class Movies():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command(aliases=['movie', 'mov'])
    async def getMovie(self, *args):
        """ Get basic info about a movie """
        self.search = tmdb.Search()

        self.response = self.search.movie(query=" ".join(args))

        self.decode = self.search.results

        if not self.decode:
            return await self.bot.say("Sorry, couldn't find that one.")

        self.rating = float(self.decode[0]['vote_average'])
        if (self.rating < 7.0):
            self.rec = "This is not a qtbot™ recommmended film."
        else:
            self.rec = "This is a qtbot™ recommended film."

        return await self.bot.say("Title: `{}`\nYear: `{}`\nPlot: `{}`\nTMDb rating: `{}`\n{}".format(self.decode[0]['title'], (self.decode[0]['release_date']).split('-')[0], self.decode[0]['overview'], self.rating, self.rec))


def setup(bot):
    bot.add_cog(Movies(bot))
