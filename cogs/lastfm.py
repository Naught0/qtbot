import json
from datetime import datetime as dt
from types import SimpleNamespace

import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw
from utils.user_funcs import PGDB


class LastFM(commands.Cog):
    URL = "http://ws.audioscrobbler.com/2.0/"
    COLOR = discord.Color.dark_red()
    TTL = 30

    def __init__(self, bot):
        self.PARAMS = {
            "method": "user.getrecenttracks",
            "api_key": bot.api_keys["lastfm"],
            "limit": 1,
            "user": None,
            "format": "json",
        }
        self.db = PGDB(bot.pg_con)
        self.redis_client = bot.redis_client
        self.session = bot.aio_session

    async def get_most_recent_track(self, lfm_user_name: str) -> dict:
        params = self.PARAMS
        params["user"] = lfm_user_name
        return await aw.aio_get_json(self.session, self.URL, params=params)

    @commands.group(aliases=["lastfm"], invoke_without_command=True)
    async def np(self, ctx: commands.Context):
        # Check for mentions
        if ctx.message.mentions:
            user_id = ctx.message.mentions[0].id
        else:
            user_id = ctx.author.id
        # Get discord member object
        member = ctx.guild.get_member(user_id)
        # Get LastFM username from DB
        lfm_user_name = await self.db.fetch_user_info(user_id, "lastfm")

        if lfm_user_name is None:
            return await ctx.error(
                f"{member.display_name} does not have a LastFM username saved"
            )

        redis_key = f"lastfm:{lfm_user_name}"
        if await self.redis_client.exists(redis_key):
            resp = json.loads(await self.redis_client.get(redis_key))
        else:
            resp = await self.get_most_recent_track(lfm_user_name)
            await self.redis_client.set(redis_key, json.dumps(resp), ex=self.TTL)

        # API error
        if resp is None:
            return await ctx.error(f"Could not get info for {lfm_user_name}.")
        # Easy dotted notation for track info
        track = SimpleNamespace(**resp["recenttracks"]["track"][0])

        em = discord.Embed(color=self.COLOR)
        em.title = f"{track.artist['#text']} - {track.name}"
        em.add_field(name="Album", value=track.album["#text"])
        # User's info for NP
        em.set_author(
            name=member.display_name, url=track.url, icon_url=member.avatar_url
        )
        # Album art
        em.set_thumbnail(url=track.image[-1]["#text"])
        # LastFM info & logo
        em.set_footer(
            text=f"LastFM: {lfm_user_name}",
            icon_url="https://www.last.fm/static/images/lastfm_avatar_applemusic.b06eb8ad89be.png",
        )
        # Time played
        em.timestamp = (
            dt.now()
            if "@attr" in resp["recenttracks"]["track"][0]
            else dt.utcfromtimestamp(int(track.date["uts"]))
        )

        await ctx.send(embed=em)

    @np.command(name="add", aliases=["user"])
    async def _add(self, ctx: commands.Context, *, user_name: str):
        if len(user_name) > 128:
            return await ctx.error("That name's a bit too long")
        await self.db.insert_user_info(ctx.author.id, "lastfm", user_name)
        await ctx.message.add_reaction("✅")


def setup(bot):
    bot.add_cog(LastFM(bot))
