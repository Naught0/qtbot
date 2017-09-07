#!/bin/evn python
import discord
import json
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

    def json_to_embed(json_dict):
        em = discord.Embed()
        em.title = json_dict['title']
        em.description = json_dict['description']
        em.url = json_dict['url']
        em.set_image(url=json_dict['urlToImage'])

        return em

    @commands.command(name='news')
    async def get_news(self, ctx):
        """ Get the top 5 articles from Google News (http://newsapi.org """

        """
        Here's my dream:
           1. Check whether cached response exists
           2. Return that information or make the API call
           3. Map each field of the json response to an embed field
                - Make the footer of the embed the page currently displayed
           - The bot sends the first article in this format from a list of pre-fabricated embeds
            - I can get the message object which was sent by assigning the ctx.send to a variable
                - Add 1 - 5 emoji reactions along with first/last buttons
                - When the user clicks on one (on_reaction_add / on_reaction_remove) go to that page with:
                    - discord.Message.edit
        """

        em_list = []

        if await self.redis_client.exists('news'):
            raw_json_string = await self.redis_client.get('news')
            raw_json_dict = json.loads(raw_json_string)
            article_list = raw_json_dict['articles']

            await self.redis_client.set('news', json.dumps(article_list), ex=300)

            for article in article_list:
                em_list.append(News.json_to_embed(article))

        else:
            raw_json_string = await self.redis_client.get('news')
            article_list = json.loads(raw_json_string)

            for article in article_list:
                em_list.append(News.json_to_embed(article))

        await ctx.send(embed=em_list[0])

def setup(bot):
    bot.add_cog(News(bot))
