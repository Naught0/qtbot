import json
import asyncio
import re
import discord
from datetime import datetime
from dateutil.parser import parse

from utils import aiohttp_wrap as aw
from discord.ext import commands


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = bot.redis_client
        self.aio_session = bot.aio_session
        self.uri = "https://newsapi.org/v2/top-headlines"
        self.api_key = bot.api_keys["news"]
        self.headers = {"X-Api-Key": self.api_key}

    @staticmethod
    def json_to_embed(json_dict: dict) -> discord.Embed:
        em = discord.Embed()
        em.title = json_dict["title"]
        em.description = json_dict["description"]
        em.url = json_dict["url"]

        # This field is empty sometimes -> handle it
        if json_dict["urlToImage"]:
            em.set_thumbnail(url=json_dict["urlToImage"])

        # This regex string brought to you by Jared :)
        pattern = "https?://(?:www\.)?(\w+).*"
        organization = re.match(pattern, json_dict["url"]).group(1)
        em.set_footer(text=json_dict["source"]["name"])
        em.timestamp = parse(json_dict["publishedAt"])

        return em

    @commands.command(name="news")
    async def get_news(
        self,
        ctx: commands.Context,
        *,
        query: commands.clean_content(escape_markdown=True) = None,
    ):
        """ Get the top 5 articles from Google News (http://newsapi.org) (Paginated) """

        # Add Emojis for navigation
        emoji_tup = tuple(f"{x}\U000020e3" for x in range(1, 10))

        em_dict = {}

        params = {"q": query, "pageSize": 9, "sources": "google-news"} if query else {"sources": "google-news", "pageSize": 9}

        redis_key = f"news:{query}" if query else "news"
        if await self.redis_client.exists(redis_key):
            raw_json_string = await self.redis_client.get(redis_key)
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict["articles"]

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_tup[idx]] = self.json_to_embed(article)

        else:
            api_response = await aw.aio_get_json(
                self.aio_session, self.uri, params=params, headers=self.headers
            )
            if api_response is None:
                return await ctx.error("API error", description="Something went wrong with that request. Try again later.")

            article_list = api_response["articles"]
            if len(article) == 0:
                return await ctx.error("No articles found", description=f"Couldn't find any news on `{query}`")
                
            await self.redis_client.set(redis_key, json.dumps(api_response), ex=10 * 60)

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_tup[idx]] = self.json_to_embed(article)

        bot_message = await ctx.send(embed=em_dict[emoji_tup[0]])

        for emoji in emoji_tup:
            await bot_message.add_reaction(emoji)

        def check(reaction, user):
            return (
                user == ctx.author
                and reaction.emoji in emoji_tup
                and reaction.message.id == bot_message.id
            )

        while True:
            try:
                reaction, user = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=60.0
                )
            except asyncio.TimeoutError:
                return await bot_message.clear_reactions()

            if reaction.emoji in em_dict:
                await bot_message.edit(embed=em_dict[reaction.emoji])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)


def setup(bot):
    bot.add_cog(News(bot))
