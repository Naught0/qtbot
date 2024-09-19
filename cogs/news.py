import asyncio
import json
import re
from typing import TypedDict

import discord
from dateutil.parser import parse
from discord.ext import commands
from utils import aiohttp_wrap as aw
from utils import custom_context


class Source(TypedDict):
    name: str
    url: str


class Article(TypedDict):
    title: str
    description: str
    content: str
    url: str
    image: str
    publishedAt: str
    source: Source


def remove_summary_char_count(summary: str) -> str:
    pat = re.compile(r"\[.*\]")
    return re.sub(pat, "", summary).strip()


def get_favicon_url(url: str) -> str:
    return f"https://www.google.com/s2/favicons?domain=${url}"


def article_to_embed(article: Article) -> discord.Embed:
    em = discord.Embed()
    em.title = article["title"]
    em.description = article["description"]
    em.url = article["url"]

    if article.get("image"):
        em.set_thumbnail(url=article["image"])

    em.set_footer(
        text=article["source"]["name"],
        icon_url=get_favicon_url(article["source"]["url"]),
    )
    em.timestamp = parse(article["publishedAt"])

    return em


class News(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = bot.redis_client
        self.aio_session = bot.aio_session
        self.uri = "https://gnews.io/api/v4{}"
        with open("data/apikeys.json") as f:
            self.api_key = json.load(f)["news"]

    @commands.command(name="news")
    async def get_news(
        self,
        ctx: custom_context.CustomContext,
        *,
        query: str | None,
    ):
        """Get the latest and greatest news or optionally search for some specific news stories"""

        # Add Emojis for navigation
        emoji_tup = tuple(f"{x}\U000020e3" for x in range(1, 10))
        if query is not None:
            query = await commands.clean_content(escape_markdown=True).convert(
                ctx, query
            )

        em_dict = {}
        params = {
            "category": "general",
            "lang": "en",
            "country": "us",
            "max": 9,
            "apikey": self.api_key,
        }

        redis_key = f"news:{query}" if query else "news"
        if await self.redis_client.exists(redis_key):
            raw_json_string = await self.redis_client.get(redis_key)
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict["articles"]

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_tup[idx]] = article_to_embed(article)

        else:
            api_response = await aw.aio_get_json(
                self.aio_session,
                self.uri.format("/search" if query else "/top-headlines"),
                params=params,
            )
            if api_response is None:
                return await ctx.error(
                    "API error",
                    description="Something went wrong with that request. Try again later.",
                )

            article_list: list[Article] = api_response["articles"]
            if len(article_list) == 0:
                return await ctx.error(
                    "No articles found",
                    description=f"Couldn't find any news on `{query}`",
                )

            await self.redis_client.set(redis_key, json.dumps(api_response), ex=10 * 60)

            for idx, article in enumerate(article_list):
                em_dict[emoji_tup[idx]] = article_to_embed(article)

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
                reaction, _ = await self.bot.wait_for(
                    "reaction_add", check=check, timeout=30.0
                )
            except asyncio.TimeoutError:
                return await bot_message.clear_reactions()

            if reaction.emoji in em_dict:
                await bot_message.edit(embed=em_dict[reaction.emoji])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)


async def setup(bot):
    await bot.add_cog(News(bot))
