import json

from types import SimpleNamespace

import discord
from bs4 import BeautifulSoup
from discord.ext import commands

from utils import aiohttp_wrap as aw
from utils.user_funcs import PGDB


class Weather(commands.Cog):
    def __init__(self, bot):
        self.weather_url = "https://api.openweathermap.org/data/2.5/weather"
        self.forecast_url = "https://api.openweathermap.org/data/2.5/forecast"
        self.icon_url = "http://openweathermap.org/img/wn/{}@2x.png"
        self.api_key = bot.api_keys["open_weather"]
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.db = PGDB(bot.pg_con)
        self.color = 0xB1D9F4
        self.cache_ttl = 3600

    @staticmethod
    def f2c(weather_data: dict) -> dict:
        """ Converts F to C and returns the dict anew """
        # if (response['sys']['country'] != 'US')
        # Celsius conversion
        weather_data["main"]["temp"] = int(
            (weather_data["main"]["temp"] - 32) * (5 / 9)
        )
        # MPH -> M/s
        weather_data["wind"]["speed"] = int(weather_data["wind"]["speed"] * 0.44704)

        return weather_data

    @commands.command(aliases=["az", "al"])
    async def add_location(self, ctx, *, location: str):
        """Add your location (zip, city, etc) to qtbot's database so
        you don't have to supply it later"""
        await self.db.insert_user_info(ctx.author.id, "zipcode", location)
        await ctx.success(f"Successfully added location `{location}`.")

    @commands.command(aliases=["rz", "rl"])
    async def remove_location(self, ctx):
        """ Remove your location from the database """
        await self.db.remove_user_info(ctx.author.id, "zipcode")
        await ctx.success(f"Successfully removed location for `{ctx.author}`.")

    @commands.command(aliases=["wt", "w"])
    async def weather(self, ctx, *, location: str = None):
        """ Get the weather of a given area (zipcode, city, etc.) """
        # Handle shortcut no location given
        if location is None:
            location = await self.db.fetch_user_info(ctx.author.id, "zipcode")
            if location is None:
                return await ctx.error(
                    "You don't have a location saved!",
                    description="Feel free to use `al` to add your location, or supply one to the command.",
                )

        # Check for redis cached response
        redis_key = f"{location}:weather"
        if await self.redis_client.exists(redis_key):
            weather_data = json.loads(await self.redis_client.get(redis_key))
        else:
            if location.isnumeric():
                weather_data = await aw.aio_get_json(
                    self.aio_session,
                    self.weather_url,
                    params={
                        "zip": location,
                        "units": "imperial",
                        "APPID": self.api_key,
                    },
                )
            else:
                weather_data = await aw.aio_get_json(
                    self.aio_session,
                    self.weather_url,
                    params={"q": location, "units": "imperial", "APPID": self.api_key},
                )
            # Check for valid response
            if weather_data is None:
                return await ctx.error(f"Sorry, couldn't find weather for {location}")

            # Add key to redis after fetching
            await self.redis_client.set(
                redis_key, json.dumps(weather_data), ex=self.cache_ttl
            )

        # Make SI conversions if needed
        if weather_data["sys"]["country"] == "US":
            celsius = False
        else:
            weather_data = self.f2c(weather_data)
            celsius = True

        # Create the embed
        em = discord.Embed(
            title=f"{weather_data['name']}, {weather_data['sys']['country']}",
            color=self.color,
        )
        em.description = weather_data["weather"][0]["description"].capitalize()
        em.add_field(
            name="Temperature",
            value=f"{int(round(weather_data['main']['temp']))}°F"
            if not celsius
            else f"{weather_data['main']['temp']}°C",
        )
        em.add_field(
            name="Wind",
            value=f"{int(round(weather_data['wind']['speed']))} MPH"
            if not celsius
            else f"{weather_data['wind']['speed']} m/s",
        )
        em.add_field(name="Humidity", value=f"{weather_data['main']['humidity']}%")
        em.set_thumbnail(url=self.icon_url.format(weather_data["weather"][0]["icon"]))

        await ctx.send(embed=em)

    @commands.command(aliases=["fc"])
    async def forecast(self, ctx, *, location: str = None):
        """ Get the forecast of a given location """
        if location is None:
            location = await self.db.fetch_user_info(ctx.author.id, "zipcode")
            if location is None:
                return await ctx.send(
                    "You don't have a location saved!",
                    description="Feel free to use `al` to add your location, or supply one to the command",
                )

        redis_key = f"{location}:forecast"
        if await self.redis_client.exists(redis_key):
            raw_weather_str = await self.redis_client.get(redis_key)
            forecast_data = json.loads(raw_weather_str)
        else:
            # Zipcode
            if location.isnumeric():
                forecast_data = await aw.aio_get_json(
                    self.aio_session,
                    self.forecast_url,
                    params={
                        "zip": location,
                        "units": "imperial",
                        "APPID": self.api_key,
                    },
                )
            else:
                forecast_data = await aw.aio_get_json(
                    self.aio_session,
                    self.forecast_url,
                    params={"q": location, "units": "imperial", "APPID": self.api_key},
                )
            # Check for valid response
            if forecast_data is None:
                return await ctx.error(
                    f"Sorry, couldn't find a forecast for {location}"
                )

            # Add key to redis after fetching
            await self.redis_client.set(
                redis_key, json.dumps(forecast_data), ex=self.cache_ttl
            )

        if forecast_data["city"]["country"] == "US":
            celsius = False
        else:
            celsius = True

        # Now make the embed
        # List contains every 3 hours, so 8 would be 24 hours from now
        _t = forecast_data["list"][8]

        if celsius:
            _t = self.f2c(_t)

        tomorrow_d = {
            "conditions": _t["weather"][0]["description"].capitalize(),
            "temp": _t["main"]["temp"],
            "humid": _t["main"]["humidity"],
            "wind": _t["wind"]["speed"],
            "icon": _t["weather"][0]["icon"],
        }

        tm = SimpleNamespace(**tomorrow_d)

        em = discord.Embed(
            title=f"The forecast for `{location}`, tomorrow", color=self.color
        )
        em.description = tm.conditions
        em.add_field(
            name="Temperature",
            value=f"{int(round(tm.temp))} \u00B0F"
            if not celsius
            else f"{int(round(tm.temp))} \u00B0C",
        )
        em.add_field(name="Humidity", value=f"{int(round(tm.humid))}%")
        em.add_field(
            name="Wind",
            value=f"{int(round(tm.wind))} MPH"
            if not celsius
            else f"{int(round(tm.wind))} M/s",
        )
        em.set_thumbnail(url=self.icon_url.format(tm.icon))

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Weather(bot))
