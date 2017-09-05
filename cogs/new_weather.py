#!/bin/env python

import discord
import aredis
import json
from utils import user_funcs as uf
from utils import aiohttp_wrap as aw
from datetime import datetime
from discord.ext import commands


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.weather_icon_dict = {} # Empty for now
        self.api_url = 'http://api.openweathermap.org/data/2.5/weather?zip={},{}&APPID={}'
        self.icon_url = "http://openweathermap.org/img/w/{weather_data['weather'][0]['icon']}.png" # for later use

        with open('data/apikeys.json') as f:
            self.api_key = json.load(f)['open_weather']

    @commands.command(name='naz')
    async def new_add_zip(self, ctx, zip_code):
        """ Add your zipcode to qtbot's database """
        if len(zip_code) != 5 or not zip_code.is_numeric():
            return await ctx.send('Please supply a valid zipcode.')

        # Add zipcode to file
        uf.update_user_info(ctx.author.id, 'zip', zip_code)

        await ctx.send(f'Successfully added zipcode `{zip_code}` for user `{str(ctx.author)}`.')

    @commands.command(name='nu_weather', aliases=['nwt'])
    async def get_weather(self, ctx, zip_code=None, region_abv='us'):
        """ Get the weather via a new source """
        start_time = datetime.now()

        if not zip_code:
            zip_code = uf.get_user_info(str(ctx.author.id), 'zip')

        # ufm function will return None in the case that the user doesn't have zip saved
        if zip_code is None:
            return await ctx.send("Sorry, you're not in my file. Please use `az` to add your zipcode, or supply one to the command.")

        # Check for cached results in redis server
        if self.redis_client.exists(f'{ctx.author.id}:weather'):
            resp = self.redis_client.get(f'{ctx.author.id}:weather')
            await ctx.send('Using cached information.')

        # Store reults in cache for 7200 seconds
        # This is the frequency with which the API updates so there's no use in querying at a faster rate
        else:
            await ctx.send('Making call -- NO cached info.')
            resp = await aw.aio_get_json(self.aio_session, self.api_url.format(zip_code, region_abv, self.api_key))
            self.redis_client.set(f'{ctx.author.id}:weather', resp, ex=7200)

        now_time = datetime.now()

        await ctx.send(f'Response:\n ```{str(resp)}```\nTime: `{str(now_time - start_time)}`')


def setup(bot):
    bot.add_cog(Weather(bot))
    