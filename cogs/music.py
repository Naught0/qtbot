import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw


class MusicInfo(commands.Cog):
    """A cog for retrieving music information (not playing it)"""

    URL = "http://ws.audioscrobbler.com/2.0/"
    LOGO_URL = "https://www.last.fm/static/images/lastfm_logo_facebook.1b63d4451dcc.png"
    NO_RESULT = "Sorry, couldn't find anything for {}."
    EM_COLOR = discord.Color.blurple()

    def __init__(self, bot):
        self.TOKEN = bot.api_keys["lastfm"]

    @staticmethod
    def truncat(text: str, length=500) -> str:
        if len(text) > length:
            return f"{text[:length - 3]}..."

        return text

    @commands.group(aliases=["lastfm", "fm"], hidden=True)
    async def music(self, ctx):
        """Main group cmd"""

    @music.command(hidden=True)
    async def album(self, ctx, *, query):
        """Search for some basic album information via album name"""
        search_params = {
            "method": "album.search",
            "album": query,
            "limit": 5,
            "format": "json",
            "api_key": self.TOKEN,
        }
        search_resp = await aw.aio_get_json(ctx.bot.aio_session, self.URL, params=search_params)

        # API didn't respond
        if search_resp is None:
            return await ctx.error("There was a problem with the last.fm API, try again later.")

        # No results
        if len(search_resp["results"]["albummatches"]["album"]) == 0:
            return await ctx.error(self.NO_RESULT.format(query))

        search_result = search_resp["results"]["albummatches"]["album"][0]
        name = search_result["name"]
        artist = search_result["artist"]

        # Once we've found the matching album, we've gotta do ANOTHER request
        info_params = {
            "method": "album.getInfo",
            "artist": artist,
            "album": name,
            "format": "json",
            "api_key": self.TOKEN,
        }
        info_resp = await aw.aio_get_json(ctx.bot.aio_session, self.URL, params=info_params)

        em = discord.Embed(
            title=f"{artist} - {name}",
            url=info_resp["album"]["url"],
            color=self.EM_COLOR,
        )
        em.set_thumbnail(url=info_resp["album"]["image"][-1]["#text"])
        # If there's some wiki info, include it
        if "wiki" in info_resp["album"]:
            em.description = self.truncat(info_resp["album"]["wiki"]["summary"])

        # Get and number the tracks in a list
        tracks = [f"{idx + 1}. {x['name']}" for idx, x in enumerate(info_resp["album"]["tracks"]["track"][:15])]
        em.add_field(name="Track List", value="\n".join(tracks))

        # Attribution or whatever
        em.set_footer(text="Powered by last.fm", icon_url=self.LOGO_URL)

        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(MusicInfo(bot))
