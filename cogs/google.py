import discord
import requests
import re
import requests_cache
import random
from cogs.utils import GoogleFuncs as gf
from discord.ext import commands

class Google():
    def __init__(self, bot):
        self.bot = bot

    # Scrapable search URL
    uri = "http://google.com/search?q={}"

    # Rotate between a few different chromium headers
    # Maybe this will help google to not block me (:
    headers = [{"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36"}, {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.1 Safari/537.36"}, {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2227.0 Safari/537.36"}]
  
    @commands.bot.command(name="google", aliases=["g", "goog"])
    async def new_google(self, *args):
        """ Get the first Google result for a query """

        # Cache results for a half hour
        requests_cache.install_cache(expire_after=1800)

        # Queries must be '+' delimited
        query = "+".join(args)

        # Why would you google for numbers / symbols?
        if not re.search("[a-z]", query, re.IGNORECASE):
            return await self.bot.say("For calculations, try `.calc`.")

        # Create google search URL
        query_url = self.uri.format(query)

        # Gather webpage
        result = requests.get(query_url, headers=self.headers[random.randint(0, len(self.headers))]).text

        # Extract links from page
        link_list = gf.get_google_links(result)

        # Say first result
        return await self.bot.say("{}".format(link_list[0]))

def setup(bot):
    bot.add_cog(Google(bot))