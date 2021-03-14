import re

import discord

from typing import Dict
from urllib.parse import quote_plus
from bs4 import BeautifulSoup as bs
from discord.ext import commands
from utils import aiohttp_wrap as aw


class Books(commands.Cog):
    URL = "https://openlibrary.org"

    def __init__(self, bot, *args, **kwargs):
        self.color = 0xB38E86
        self.bot = bot
        self.session = bot.aio_session

    def get_first_result(self, soup: bs) -> Dict:
        res = soup.select_one("li.searchResultItem")
        return {
            "image_url": res.select_one("span.bookcover img")["src"],
            "title": res.select_one("h3.booktitle a").text.title().strip(),
            "book_url": res.select_one("h3.booktitle a")["href"],
            "author": res.select_one("span.bookauthor a").text.strip(),
        }

    def get_book_info(self, soup: bs) -> Dict:
        return {
            "description": soup.select_one("div.book-description-content p").text.strip(),
            "isbn": soup.select_one('dd[itemprop="isbn"]').text.strip(),
            "published": soup.select_one("p.first-published-date").text.strip(),
        }

    def to_embed(self, book_info) -> discord.Embed:
        year = re.search(r"(in )(\d+)", book_info["published"]).group(2)
        em = discord.Embed()
        em.color = self.color
        em.title = f"{book_info['title']} by {book_info['author']} ({year})"
        em.url = f"{self.URL}{book_info['book_url']}"
        em.description = book_info["description"]
        em.add_field(name="ISBN", value=book_info["isbn"])
        em.set_thumbnail(url=f"https:{book_info['image_url']}")

        return em

    @commands.command(name="book", aliases=["books"])
    async def _book(self, ctx: commands.Context, *, title: str):
        resp = await aw.aio_get_text(
            self.session, f"{self.URL}/search?title={quote_plus(title)}"
        )
        soup = bs(resp, features="lxml")

        if soup.select_one("span.red"):
            return await ctx.error(f"{title.title()} not found")

        book_info = self.get_first_result(soup)
        resp = await aw.aio_get_text(self.session, f"{self.URL}{book_info['book_url']}")
        soup = bs(resp, features="lxml")
        book_info.update(**self.get_book_info(soup))
        
        await ctx.send(embed=self.to_embed(book_info))


def setup(bot):
    bot.add_cog(Books(bot))
