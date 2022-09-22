from datetime import datetime
from pprint import pprint
import re

import discord
import aiohttp

from typing import Dict, List
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as bs
from discord.ext import commands
from utils import aiohttp_wrap as aw
from utils.paginate import paginate
from utils.dict_manip import dig


class Books(commands.Cog):
    URL = "https://www.googleapis.com/books/v1"

    def __init__(self, bot, *args, **kwargs):
        self.color = 0xB38E86
        self.bot = bot
        self.session: aiohttp.ClientSession = bot.aio_session

    def make_embeds(self, books: List[dict]) -> discord.Embed:
        ret = []
        for idx, book in enumerate(books):
            volume_info = book["volumeInfo"]

            categories = ", ".join(volume_info.get("categories", []))
            description = volume_info.get("description")
            authors = volume_info.get("authors")
            date = volume_info.get("publishedDate")
            thumbnail = dig(
                volume_info,
                "imageLinks",
                "thumbnail",
                default="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/240/twitter/282/blue-book_1f4d8.png",
            )
            page_count = volume_info.get("pageCount")
            idents = [
                {"name": x["type"], "value": f"`{x['identifier']}`"}
                for x in book["volumeInfo"].get("industryIdentifiers", [])[:3]
            ]
            rating = volume_info.get("averageRating", "???")
            rating_count = volume_info.get("ratingsCount", 0)

            em = discord.Embed(
                description=description,
                title=volume_info["title"][:256],
                color=self.color,
                url=volume_info["canonicalVolumeLink"],
            )
            if authors:
                em.add_field(name="Author" if len(authors) == 1 else "Authors", value=", ".join(authors))
            if date:
                em.add_field(name="Published date", value=date, inline=True)
            if categories:
                em.add_field(name="Categories", value=categories, inline=True)
            em.add_field(name="Page count", value=page_count)
            for id in idents:
                em.add_field(name=id["name"], value=id["value"], inline=True)
            if rating and rating_count:
                em.add_field(name="Ratings", value=f"{rating} / 5 ({rating_count} ratings)")
            em.set_thumbnail(url=thumbnail)
            em.set_footer(text=f"{idx + 1} / {len(books)}")

            ret.append(em)

        return ret

    @commands.command(name="book", aliases=["books"])
    async def _book(self, ctx: commands.Context, *, search: str):
        resp = await aw.aio_get_json(self.session, f"{self.URL}/volumes", params={"q": search, "maxResults": 5})
        if resp is None:
            return await ctx.error("Couldn't find a matching book")

        embeds = self.make_embeds(resp["items"])
        msg = await ctx.send(embed=embeds[0])
        await paginate(ctx, msg, embeds)


def setup(bot):
    bot.add_cog(Books(bot))
