import discord

from urllib.parse import quote_plus
from bs4 import BeautifulSoup as bs
from discord.ext import commands
from utils import aiohttp_wrap as aw


class Books(commands.Cog):
    URL = "https://openlibrary.org/"

    def __init__(self, bot, *args, **kwargs):
        self.color = 0xB38E86
        self.bot = bot
        self.session = bot.aio_session

    def get_first_result(self, soup: bs):
        res = soup.select_one('li.searchResultItem')
        return {
            'image_url': res.select_one('span.bookcover img')['src'],
            'title': res.select_one('h3.booktitle a').text.title(),
            'book_url': res.select_one('h3.booktitle a')['href'],
            'author': res.select_one('span.bookauthor a').text
        }
    
    def get_book_info(self, soup: bs):
        pass

    @commands.command(name="book", aliases=["books"])
    async def _book(self, ctx: commands.Context, *, title: str):
        resp = await aw.aio_get_text(self.session, f"{self.URL}search?title={quote_plus(title)}")
        search_soup = bs(resp)

        if search_soup("span.red", text="No results found."):
            return await ctx.error(f"{title.title()} not found")
        
        await ctx.send(f"```{self.get_first_result(search_soup)}```")
        


def setup(bot):
    bot.add_cog(Books(bot))
