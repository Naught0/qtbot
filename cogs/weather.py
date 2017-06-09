import discord, json, requests, requests_cache
from cogs.utils import UserFileManip as ufm
from discord.ext import commands

class Weather():
    def __init__(self, bot):
        self.bot = bot

    # Wunderground API info
    with open("data/apikeys.json", "r") as f:
        apiKeys = json.load(f)
    f.close()
    wunderZipURL = "http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json"
    wunderKey = apiKeys['wunderground']

    @commands.bot.command(pass_context = True, aliases = ['addzip', 'addz, ''az'])
    async def addZipCode(self, ctx, zip_code = ""):
        """ Add your zipcode for qtbot to remember """

        # No zipcode supplied
        if (zip_code == "" ):
            return await self.bot.say("Please supply a zipcode.")
        # Invalid zip supplied
        if (len(zip_code) != 5 or not zip_code.isnumeric()):
            return await self.bot.say("Please supply a valid zipcode.")

        # Get user ID
        self.member = str(ctx.message.author)

        # Add zipcode to file
        ufm.updateUserInfo(self.member, "zip", zip_code)

        return await self.bot.say("Successfully added zipcode `{}` for user `{}`.".format(zip_code, self.member))

    # Gets weather based on zip
    @commands.bot.command(pass_context = True, aliases = ['wt', 'w'])
    async def weather(self, ctx, zip_code = ""):
        """ 
        Search with zipcode, or not, and qtbot will try to find your zip from the userfile.
        """
        # Set cache expiry time
        requests_cache.install_cache(expire_after=1800)

        # user's snowflake ID
        self.member = str(ctx.message.author)

        # Inits file if not found
        if not ufm.foundUserFile():
            ufm.createUserFile(self.member, "zip", zip_code)
        elif zip_code == "": # Find zipcode in file
            zip_code = ufm.getUserInfo(self.member, "zip")
        
        # getUserInfo returns "error" if user has no zip on file
        if zip_code == "error":
            return await self.bot.say("Sorry, you're not in my file!\nPlease use `addzip` `addz` or `az` with a zipcode.")

        # Load wunderAPI info into d
        # Sometimes wunderground dies --> handle it
        try:
            self.d = requests.get(Weather.wunderZipURL.format(Weather.wunderKey, zip_code)).json()
        except ConnectionError as e:
            return await self.bot.say("Sorry, wunderground is having trouble with this request.\n{}".format(e))
        
        # Except KeyError --> city isn't found 
        try:
            self.city = self.d["location"]["city"]
        except KeyError:
            return await self.bot.say("Sorry, I'm having trouble finding your location.")

        # Store the relevant parts of the call in strings
        self.state = self.d["location"]["state"]
        self.temp = self.d["current_observation"]["temp_f"]
        self.conditions = self.d["current_observation"]["weather"]
        self.wind = self.d["current_observation"]["wind_string"]
        self.humidity = self.d["current_observation"]["relative_humidity"]

        return await self.bot.say("The weather for `{}, {}`: \n`{}` at `{}°F`. Winds `{}`. Relative humidity `{}`.".format(self.city, self.state, self.conditions, self.temp, self.wind.lower(), self.humidity))

    # Gets forecast based on zip
    @commands.bot.command(pass_context = True, aliases = ['fc', 'f'])
    async def forecast(self, ctx, zip_code = ""):
        """ 
        Search with zipcode, or not, and qtbot will try to find your zip from the userfile.
        """ 
        # Set cache expiry time
        requests_cache.install_cache(expire_after=3600)

        # user's snowflake ID
        self.member = str(ctx.message.author)   
        
        # Inits userfile if not found with given values
        if not ufm.foundUserFile():
            ufm.createUserFile(self.member, "zip", zip_code)
        elif zip_code == "": # Find zipcode in file
            zip_code = ufm.getUserInfo(self.member, "zip")
        
        # getUserInfo returns "error" if user has no zip on file
        if zip_code == "error":
            return await self.bot.say("Sorry, you're not in my file!\nPlease use `addzip` `addz` or `az` with a zipcode.")

        # Json response in string form
        self.d = requests.get(Weather.wunderZipURL.format(Weather.wunderKey, zip_code)).json()
        
        # Handling city not found error
        try:
            self.city = self.d["location"]["city"]
        except KeyError:
            return await self.bot.say("Sorry, I'm having trouble finding your location.")
        
        # Load forecasts into strings
        self.foreTom = self.d["forecast"]["txt_forecast"]["forecastday"][2]["fcttext"]
        self.foreTomNight = self.d["forecast"]["txt_forecast"]["forecastday"][3]["fcttext"]

        return await self.bot.say("Tomorrow: `{}`\nTomorrow Evening: `{}`".format(self.foreTom, self.foreTomNight))

def setup(bot):
    bot.add_cog(Weather(bot))