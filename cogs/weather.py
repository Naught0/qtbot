import discord
import json
import requests
import requests_cache
from cogs.utils import UserFileManip as ufm
from discord.ext import commands

# Wunderground API info
with open("data/apikeys.json", "r") as f:
    api_key = json.load(f)["wunderground"]

weather_icon_dict = {"storm": "https://u.teknik.io/gXqry.png", "partly_cloudy": "https://u.teknik.io/Va3lK.png", "mostly_cloudy": "https://u.teknik.io/GZVKi.png",
                     "cloudy": "https://u.teknik.io/xG1R0.png", "clear": "https://u.teknik.io/ddab9.png", "rain": "https://u.teknik.io/HdThS.png"}

wunderground_url = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"


class Weather:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="az")
    async def add_zip(self, ctx, zip_code=""):
        """ Add your zipcode for qtbot to remember """

        # No zipcode supplied
        if (zip_code == ""):
            return await ctx.send("Please supply a zipcode.")
        # Invalid zip supplied
        if (len(zip_code) != 5 or not zip_code.isnumeric()):
            return await ctx.send("Please supply a valid zipcode.")

        # Get user ID
        member = str(ctx.message.author)

        # Add zipcode to file
        ufm.updateUserInfo(member, "zip", zip_code)

        await ctx.send("Successfully added zipcode `{}` for user `{}`.".format(zip_code, member))

    # Gets weather based on zip
    @commands.command(name="wt", aliases=['w'])
    async def weather(self, ctx, zip_code=""):
        """ Search with zipcode, or not, and qtbot will try to find your zip from the userfile. """

        # Set cache expiry time
        requests_cache.install_cache(expire_after=1800)

        # user's snowflake ID
        member = str(ctx.message.author)

        # If no zipcode provided
        if zip_code == "":  # Find zipcode in file
            zip_code = ufm.getUserInfo(member, "zip")

        # getUserInfo returns "error" if user has no zip on file
        if zip_code == "error":
            return await ctx.send("Sorry, you're not in my file!\nPlease use `addzip` `addz` or `az` with a zipcode.")

        # Load wunderAPI info into d
        # Sometimes wunderground dies --> handle it
        try:
            d = requests.get(wunderground_url.format(
                api_key, zip_code)).json()
        except ConnectionError:
            return await ctx.send("Sorry, wunderground is having trouble with this request. Try again in a bit.")

        # Except KeyError --> city isn't found
        try:
            city = d["location"]["city"]
        except KeyError:
            return await ctx.send("Sorry, I'm having trouble finding your location.")

        # Store the relevant parts of the call in strings
        state = d["location"]["state"]
        temp = d["current_observation"]["temp_f"]
        conditions = d["current_observation"]["weather"]
        wind = d["current_observation"]["wind_string"]
        humidity = d["current_observation"]["relative_humidity"]

        # Create the embed
        em = discord.Embed()
        em.title = "Weather for {}, {}".format(city, state)
        em.add_field(name="Temperature", value="{}°F".format(temp))
        em.add_field(name="Conditions", value=conditions)
        em.add_field(name="Relative humidity", value=humidity)
        em.add_field(name="Winds", value=wind)

        # Conditions to lower
        cond_lower = conditions.lower()
        if "rain" in cond_lower:
            em.set_thumbnail(url=weather_icon_dict["rain"])
        elif "clear" in cond_lower or "sunny" in cond_lower:
            em.set_thumbnail(url=weather_icon_dict["clear"])
        elif "cloudy" in cond_lower:
            em.set_thumbnail(url=weather_icon_dict["partly_cloudy"])
        elif "storm" in cond_lower or "thunderstorm" in cond_lower:
            em.set_thumbnail(url=weather_icon_dict["storm"])

        await ctx.send(embed=em)

    # Gets forecast based on zip
    @commands.command(name="fc", aliases=['f'])
    async def forecast(self, ctx, zip_code=""):
        """ Search with zipcode, or not, and qtbot will try to find your zip from the userfile."""

        # Set cache expiry time
        requests_cache.install_cache(expire_after=3600)

        # user's snowflake ID
        member = str(ctx.message.author)

        # If no zipcode provided
        if zip_code == "":  # Find zipcode in file
            zip_code = ufm.getUserInfo(member, "zip")

        # UFM returns str error if no zip found
        if zip_code == "error":
            return await ctx.send("Sorry, you're not in my file!\nPlease use `addzip||addz||az` with a valid zipcode.")

        # Json response in string form
        d = requests.get(wunderground_url.format(
            api_key, zip_code)).json()

        # Handling city not found error
        try:
            city = d["location"]["city"]
        except KeyError:
            return await ctx.send("Sorry, I'm having trouble finding your location.")

        # Load forecasts into strings
        foreTom = d["forecast"]["txt_forecast"]["forecastday"][2]["fcttext"]
        foreTomNight = d["forecast"]["txt_forecast"]["forecastday"][3]["fcttext"]

        await ctx.send("Tomorrow: `{}`\nTomorrow Evening: `{}`".format(foreTom, foreTomNight))


def setup(bot):
    bot.add_cog(Weather(bot))
