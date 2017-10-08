#!/bin/env python

import discord
import json
from utils import aiohttp_wrap as aw
from discord.ext import commands
from utils.user_funcs import PGDB


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.db = PGDB(bot.pg_con)
        self.api_url = 'http://api.openweathermap.org/data/2.5/weather?zip={},{}&APPID={}'
        self.wunder_api_url = 'http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json'

        with open('data/apikeys.json') as fp:
            api_keys = json.load(fp)

        self.wunder_api_key = api_keys['wunderground']
        self.api_key = api_keys['open_weather']

    @commands.command(name='az')
    async def add_zip(self, ctx, zip_code):
        """ Add your zipcode to qtbot's database so you don't have to supply it later """
        await self.db.insert_user_info(ctx.author.id, 'zipcode', zip_code)
        await ctx.send(f'Successfully added zipcode `{zip_code}`.')

    @commands.command(name='rz')
    async def remove_zip(self, ctx):
        """ Remove your zipcode from the database """
        await self.db.remove_user_info(ctx.author.id, 'zipcode')
        await ctx.send(f'Successfully removed zipcode for `{str(ctx.author)}`.')

    @commands.command(name='wt')
    async def get_weather(self, ctx, zip_code='', region_abv='us'):
        """ Get the weather via zipcode """
        if not zip_code:
            zip_code = await self.db.fetch_user_info(ctx.author.id, 'zipcode')

        # DB function will return None in the case that the user doesn't have zip saved
        if zip_code is None:
            return await ctx.send(
                "Sorry, you're not in my file. Please use `az` to add your zipcode, or supply one to the command.")

        # Check for cached results in redis server
        if await self.redis_client.exists(f'{zip_code}:weather'):
            owm_data = await self.redis_client.get(f'{zip_code}:weather')
            owm_data = json.loads(owm_data)

        # Store reults in cache for 7200 seconds
        # This is the frequency with which the API updates so there's no use in querying at a faster rate
        else:
            owm_data = await aw.aio_get_json(self.aio_session, self.api_url.format(zip_code, region_abv, self.api_key))

            if not owm_data:
                return await ctx.send(f"Sorry, I couldn't find weather for `{zip_code}`.")

            await self.redis_client.set(f'{zip_code}:weather', json.dumps(owm_data), ex=7200)

        # Create the embed
        em = discord.Embed()
        em.title = f"Weather for {owm_data['name']}"
        # Yeah this converts from Kevlin to Fahrenheit...
        em.add_field(name='Temperature', value=f"{float((owm_data['main']['temp'] - 273) * 1.8 + 32):.1f}°F")
        em.add_field(name='Conditions', value=f"{owm_data['weather'][0]['description'].capitalize()}")
        em.add_field(name='Humidity', value=f"{owm_data['main']['humidity']}%")
        em.add_field(name='Winds', value=f"{float(owm_data['wind']['speed']) * 2.237:.2f}mph")
        em.set_thumbnail(url=f"http://openweathermap.org/img/w/{owm_data['weather'][0]['icon']}.png")

        await ctx.send(embed=em)

    @commands.command(name='fc')
    async def get_forecast(self, ctx, zip_code=''):
        """ Get the forecast via zipcode """
        if zip_code == '':
            zip_code = await self.db.fetch_user_info(ctx.author.id, 'zipcode')

        if zip_code is None:
            return await ctx.send(
                "Sorry, you're not in my file. Please use `az` to add your zipcode, or supply one to the command.")

        # Check for cached results in redis server
        if await self.redis_client.exists(f'{zip_code}:forecast'):
            forecast_data = await self.redis_client.get(f'{zip_code}:forecast')
            forecast_data = json.loads(forecast_data)

        # Store reults in cache for 7200 seconds
        # This is the frequency with which the API updates so there's no use in querying at a faster rate
        else:
            resp = await aw.aio_get_json(self.aio_session, self.wunder_api_url.format(self.wunder_api_key, zip_code))

            # Handling CityNotFound exception
            if not ('location' in resp and 'city' in resp['location']):
                return await ctx.send("Sorry, I'm having trouble finding your location.")

            # Compresses the call into something more managable and less wasteful than the whole mess of json it gives
            forecast_data = resp['forecast']['txt_forecast']['forecastday']
            await self.redis_client.set(f'{zip_code}:forecast', json.dumps(forecast_data), ex=7200)

        await ctx.send(
            f"Tomorrow: `{forecast_data[2]['fcttext']}`\nTomorrow Evening: `{forecast_data[3]['fcttext']}`")


def setup(bot):
    bot.add_cog(Weather(bot))
