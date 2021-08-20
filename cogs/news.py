import json
import asyncio
import discord

from urllib.parse import quote
from dateutil.parser import parse

from utils import aiohttp_wrap as aw
from discord.ext import commands


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = bot.redis_client
        self.aio_session = bot.aio_session
        self.uri = "http://api.mediastack.com/v1/news"
        with open("data/apikeys.json") as f:
            self.api_key = json.load(f)["news"]

    @staticmethod
    def json_to_embed(json_dict: dict) -> discord.Embed:
        em = discord.Embed()
        em.title = json_dict["title"]
        em.description = json_dict["description"]
        em.url = json_dict["url"]

        # This field is empty sometimes -> handle it
        if json_dict["image"]:
            em.set_thumbnail(url=json_dict["image"])

        em.set_footer(text=json_dict["source"])
        em.timestamp = parse(json_dict["published_at"])

        return em

    @commands.command(name="news")
    async def get_news(
        self,
        ctx: commands.Context,
        *,
        query: commands.clean_content(escape_markdown=True) = None,
    ):
        """Get the latest and greatest news or optionally search for some specific news stories"""

        # Add Emojis for navigation
        emoji_tup = tuple(f"{x}\U000020e3" for x in range(1, 10))

        em_dict = {}

        params = (
            {
                "keywords": quote(query),
                "languages": "en",
                "limit": 9,
                "sort": "popularity",
                "access_key": self.api_key,
            }
            if query
            else {
                "languages": "en",
                "limit": 9,
                "sort": "popularity",
                "access_key": self.api_key,
            }
        )

        redis_key = f"news:{query}" if query else "news"
        if await self.redis_client.exists(redis_key):
            raw_json_string = await self.redis_client.get(redis_key)
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict["data"]

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_tup[idx]] = self.json_to_embed(article)

        else:
            api_response = await aw.aio_get_json(
                self.aio_session,
                self.uri,
                params=params,
            )
            if api_response is None:
                return await ctx.error(
                    "API error",
                    description="Something went wrong with that request. Try again later.",
                )

            article_list = api_response["data"]
            if len(article_list) == 0:
                return await ctx.error(
                    "No articles found",
                    description=f"Couldn't find any news on `{query}`",
                )

            await self.redis_client.set(redis_key, json.dumps(api_response), ex=10 * 60)

            for idx, article in enumerate(article_list):
                em_dict[emoji_tup[idx]] = self.json_to_embed(article)

        bot_message = await ctx.send(embed=em_dict[emoji_tup[0]])

        for emoji in emoji_tup[: len(article_list)]:
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
                    "reaction_add", check=check, timeout=30.0
                )
            except asyncio.TimeoutError:
                return await bot_message.clear_reactions()

            if reaction.emoji in em_dict:
                await bot_message.edit(embed=em_dict[reaction.emoji])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)


def setup(bot):
    bot.add_cog(News(bot))
