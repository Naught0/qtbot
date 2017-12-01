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
        self.locale_abv_dict = {'metric': {'temp': '°C', 'dt': 'm/s'}, 
                                'imperial': {'temp': '°F', 'dt': 'mph'}, 
                                'kelvin': {'temp': 'K', 'dt': 'm/s'}}
        self.owm_url = 'http://api.openweathermap.org/data/2.5/weather'
        self.wunder_url = 'http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json'
        self.cache_ttl = 3600

        with open('data/apikeys.json') as fp:
            api_keys = json.load(fp)

        self.wunder_api_key = api_keys['wunderground']
        self.api_key = api_keys['open_weather']

    @commands.command(name='az')
    async def add_zip(self, ctx, zip_code, region='us'):
        """ Add your zipcode to qtbot's database so you don't have to supply it later """
        await self.db.insert_user_info(ctx.author.id, 'zipcode', f'{zip_code},{region}')
        await ctx.send(f'Successfully added zipcode `{zip_code}`.')

    @commands.command(name='rz')
    async def remove_zip(self, ctx):
        """ Remove your zipcode from the database """
        await self.db.remove_user_info(ctx.author.id, 'zipcode')
        await ctx.send(f'Successfully removed zipcode for `{str(ctx.author)}`.')

    @commands.command(name='wt')
    async def get_weather(self, ctx, zip_code='', region='us'):
        """ Get the weather via zipcode, default region US"""
        if not zip_code:
            zip_code = await self.db.fetch_user_info(ctx.author.id, 'zipcode')

        # DB function will return None in the case that the user doesn't have zip saved
        if zip_code is None:
            return await ctx.send(
                "Sorry, you're not in my file. Please use `az` to add your zipcode, or supply one to the command.")

        # This is the format the OWM expects. US is the default.
        formatted_zip = f'{zip_code},{region}'

        # Get the OWM units param for the call if one is to be made
        # This is also used later to determine °F or °C and m/s vs mph
        units = 'imperial' if region.lower() in ['us', 'usa'] else 'metric'

        redis_key = f'{zip_code}:{units}:weather'
        # Check for cached results in redis server
        if await self.redis_client.exists(redis_key):
            owm_data = await self.redis_client.get(redis_key)
            owm_data = json.loads(owm_data)

        # Store reults in cache
        # The API updates every 7200 seconds
        else:
            params = {'zip': formatted_zip, 'APPID': self.api_key, 'units': units}
            owm_data = await aw.aio_get_json(self.aio_session, self.owm_url, params=params)

            if not owm_data:
                return await ctx.send(f"Sorry, I couldn't find weather for `{zip_code}`.")

            await self.redis_client.set(redis_key, json.dumps(owm_data), ex=self.cache_ttl)

        # Create the embed
        em = discord.Embed(title=f"Weather for {owm_data['name']}", color=discord.Color.dark_orange())
        em.add_field(name='Temperature', 
                     value=f"{float(owm_data['main']['temp']):.2f}{self.locale_abv_dict[units]['temp']}") 
        em.add_field(name='Conditions', value=f"{owm_data['weather'][0]['description'].capitalize()}")
        em.add_field(name='Humidity', value=f"{owm_data['main']['humidity']}%")
        em.add_field(name='Winds', value=f"{float(owm_data['wind']['speed']):.2f}" 
                                         f"{self.locale_abv_dict[units]['dt']}")
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

        # Store reults in cache 
        else:
            resp = await aw.aio_get_json(self.aio_session, self.wunder_url.format(self.wunder_api_key, zip_code))

            # Handling CityNotFound exception
            if not ('location' in resp and 'city' in resp['location']):
                return await ctx.send("Sorry, I'm having trouble finding your location.")

            # Compresses the call into something more managable and less wasteful than the whole mess of json it gives
            forecast_data = resp['forecast']['txt_forecast']['forecastday']
            await self.redis_client.set(f'{zip_code}:forecast', json.dumps(forecast_data), ex=self.cache_ttl)

        await ctx.send(
            f"Tomorrow: `{forecast_data[2]['fcttext']}`\nTomorrow Evening: `{forecast_data[3]['fcttext']}`")


def setup(bot):
    bot.add_cog(Weather(bot))
