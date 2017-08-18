#!/bin/env python

import discord
from discord.ext import commands
from utils import aiohttp_wrap as awp

"""

UNFINISHED AND NOT YET TESTED

"""

class DuckDuckGo:
    def __init__(self, bot):
        self.bot = bot
        self.base_uri = "http://api.duckduckgo.com/?q={}&format=json&t=qtbot-1.0-discord-bot"
        self.headers = headers = [{"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}, {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"}, "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"}]

    @commands.command(name="ddg", aliases=["dg"])
    async def duckduckgo_search(self, ctx, *, query):
    """ Scrape DDG since Google hates me """

    # Space delimited query
    query = query.replace(' ', '+')

    return
