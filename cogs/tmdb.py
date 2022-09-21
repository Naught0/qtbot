import discord
import json

from json.decoder import JSONDecodeError
from urllib import parse
from typing import Dict
from dateutil.parser import parse
from urllib.parse import quote_plus

from discord.ext import commands
from bs4 import BeautifulSoup
from utils.aiohttp_wrap import aio_get_json as get_json, aio_get_text as get_text


class MyTMDb(commands.Cog):
    URL = "https://api.themoviedb.org/3"
    RT_URL = "https://www.rottentomatoes.com/search"

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        with open("data/apikeys.json") as f:
            self.API_KEY = json.load(f)["tmdb"]

    async def req(self, type: str, query: str) -> Dict:
        """Wraper for TMDB requests which also fetches RottenTomatoes scores

        Args:
            type (str): movie || show
            query (str): search term

        Returns:
            Dict: API response
        """
        params = {"api_key": self.API_KEY, "query": quote_plus(query)}
        tmdb_resp = await get_json(self.session, f"{self.URL}/search/{type}", params=params)
        # Short circuit if we don't find anything from the tmdb api
        if not tmdb_resp["results"]:
            return None

        rt_resp = await get_text(self.session, self.RT_URL, params={"search": quote_plus(query)})

        tmdb_result = tmdb_resp["results"][0]
        soup = BeautifulSoup(rt_resp, "lxml")
        try:
            items = (
                json.loads(soup.select("#movies-json")[0].contents[0])["items"]
                if type == "movie"
                else json.loads(soup.select("#tvs-json")[0].contents[0])["items"]
            )
        except (JSONDecodeError, TypeError, IndexError):
            items = None

        if items:
            # Get the RT match which either is an exact match of the title & failing that, year
            # next() grabs the first result so as not to receive another array
            rt_match = next(
                filter(
                    lambda r: r["name"] == (tmdb_result["title"] if type == "movie" else tmdb_result["name"])
                    or (
                        int(r["releaseYear"]) == parse(tmdb_result["release_date"]).year
                        if "releaseYear" in r
                        else False
                    ),
                    items,
                ),
                None,
            )
        else:
            rt_match = None

        return {**tmdb_result, "rotten_tomatoes": rt_match}

    @staticmethod
    def _to_embed(result, type):
        # Get qtbot rating
        rating = float(result["vote_average"])
        if rating > 7.0:
            rec = f"This is a qtbot™ recommended {type}."
        else:
            rec = f"This is not a qtbot™ recommmended {type}."

        # Create embed
        em = discord.Embed(color=discord.Color.greyple())
        em.title = f'{result["name"] if type == "show" else result["title"]} ({parse(result["first_air_date"]).year if type == "show" else parse(result["release_date"]).year})'
        em.description = (
            f'{result["overview"]}\n\n[Rotten Tomatoes]({result["rotten_tomatoes"]["url"]})'
            if result["rotten_tomatoes"]
            else result["overview"]
        )
        em.set_thumbnail(url=f"https://image.tmdb.org/t/p/w500{result['poster_path']}")
        em.add_field(name="TMDb Rating", value=str(rating))
        if result["rotten_tomatoes"]:
            if any(
                (
                    "score" in result["rotten_tomatoes"]["audienceScore"],
                    "score" in result["rotten_tomatoes"]["tomatometerScore"],
                )
            ):
                em.add_field(
                    name="Rotten Tomatoes",
                    value=f"{':tomato: ' + result['rotten_tomatoes']['tomatometerScore']['score'] + '%' if 'score' in result['rotten_tomatoes']['tomatometerScore'] else ''} {':popcorn: ' + result['rotten_tomatoes']['audienceScore']['score'] + '%' if 'score' in result['rotten_tomatoes']['audienceScore'] else ''}",
                )
        em.set_footer(text=rec)

        return em

    @commands.command(name="show", aliases=["ss", "tv"])
    async def get_show(self, ctx, *, query):
        """Get TV show information"""

        result = await self.req("tv", query)

        # If no result are found
        if not result:
            return await ctx.error(f"Couldn't find anything for {query}")

        em = self._to_embed(result, "show")
        await ctx.send(embed=em)

    @commands.command(name="movie", aliases=["mov"])
    async def get_movie(self, ctx, *, query):
        """Get movie information"""
        result = await self.req("movie", query)

        if not result:
            return await ctx.error(f"Couldn't find anything for {query}")

        em = self._to_embed(result, "movie")
        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(MyTMDb(bot))
