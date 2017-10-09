#!/bin/evn python
import json
import asyncio
import re
import discord
from datetime import datetime
from utils import aiohttp_wrap as aw
from discord.ext import commands


class News:
    def __init__(self, bot):
        self.bot = bot
        self.redis_client = bot.redis_client
        self.aio_session = bot.aio_session
        self.uri = 'https://newsapi.org/v1/articles?source=google-news&sortBy=top&apiKey={}'
        with open('data/apikeys.json') as f:
            self.api_key = json.load(f)['news']


    @staticmethod
    def json_to_embed(json_dict: dict) -> discord.Embed:
        em = discord.Embed()
        em.title = json_dict['title']
        em.description = json_dict['description']
        em.url = json_dict['url']

        # The API returns some http shortcuts that don't place nicely with d.py
        if json_dict['urlToImage'].startswith('//'):
            em.set_image(url=f'http:{json_dict["urlToImage"]}')
        else:
            em.set_image(url=json_dict['urlToImage'])

        em.set_thumbnail(
            url='http://icons.iconarchive.com/icons/dtafalonso/android-lollipop/512/News-And-Weather-icon.png')

        # This regex string brought to you by Jared :)
        pattern = 'https?://(?:www\.)?(\w+).*'
        organization = re.match(pattern, json_dict['url']).group(1)
        em.set_footer(text=organization.upper())

        em.timestamp = datetime.strptime(re.sub('[TZ]', '', json_dict['publishedAt']), '%Y-%m-%d%H:%M:%S')

        return em

    @commands.command(name='news')
    async def get_news(self, ctx):
        """ Get the top 5 articles from Google News (http://newsapi.org) (Paginated) """

        # Add Emojis for navigation
        emoji_map = ['1\U000020e3',
                     '2\U000020e3',
                     '3\U000020e3',
                     '4\U000020e3',
                     '5\U000020e3',
                     '6\U000020e3',
                     '7\U000020e3',
                     '8\U000020e3',
                     '9\U000020e3']

        em_dict = {}

        if await self.redis_client.exists('news'):
            raw_json_string = await self.redis_client.get('news')
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict['articles']

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_map[idx]] = self.json_to_embed(article)

        else:
            api_response = await aw.aio_get_json(self.aio_session, self.uri.format(self.api_key))
            article_list = api_response['articles']
            await self.redis_client.set('news', json.dumps(api_response), ex=300)

            for idx, article in enumerate(article_list[:9]):
                em_dict[emoji_map[idx]] = self.json_to_embed(article)

        bot_message = await ctx.send(embed=em_dict[emoji_map[0]])

        for emoji in emoji_map:
            await bot_message.add_reaction(emoji)

        def check(reaction, user):
            return user == ctx.author and reaction.emoji in emoji_map

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=60.0)
            except asyncio.TimeoutError:
                return await bot_message.clear_reactions()

            if reaction.emoji in em_dict:
                await bot_message.edit(embed=em_dict[reaction.emoji])
                await bot_message.remove_reaction(reaction.emoji, ctx.author)


def setup(bot):
    bot.add_cog(News(bot))
