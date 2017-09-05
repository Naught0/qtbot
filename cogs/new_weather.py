#!/bin/env python

import discord
import json
from utils import aiohttp_wrap as aw
from utils import user_funcs as ufm
from datetime import datetime
from discord.ext import commands
from aiocache import cached

class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.weather_icon_dict = {} # Empty for now
        self.api_url = 'http://api.openweathermap.org/data/2.5/weather?zip={},{}&APPID={}'
        self.icon_url = "http://openweathermap.org/img/w/{weather_data['weather'][0]['icon']}.png" # for later use

        with open('data/apikeys.json') as f:
            self.api_key = json.load(f)['open_weather']

    @commands.command(name='nu_weather', aliases=['nwt'])
    @cached(ttl=7200)
    async def get_weather(self, ctx, zip_code=None):
        """ Get the weather via a new source """
        if not zip_code:
            zip_code = ufm.get_user_info(str(ctx.author), 'zip')

        # ufm function will return None in the case that the user doesn't have zip saved
        if zip_code is None:
            return await ctx.send("Sorry, you're not in my file. Please use `az` to add your zipcode, or supply one to the command.")


        resp = await aw.aio_get_json(self.aio_session, self.api_url.format('33073', 'us', self.api_key))

        now_time = datetime.now()

        await ctx.send(f'Response:\n ```{resp}```\nTime: `{str(now_time - start_time)}`')


def setup(bot):
    bot.add_cog(Weather(bot))
    