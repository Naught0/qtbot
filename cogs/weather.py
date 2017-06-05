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

    # Gets weather based on zip
    @commands.bot.command(pass_context=True)
    async def wt(self, ctx, zipCode = ""):
        """ 
        search via zip code and qtbot will remember you next time
        """
        # Set cache expiry time
        requests_cache.install_cache(expire_after=1800)

        # user's snowflake ID
        self.member = str(ctx.message.author)

        # Inits file if not created yet w/ user info
        if not ufm.foundUserFile():
            ufm.createUserFile(self.member, "zip", zipCode)

        # Find zip in file
        if zipCode == "":
            zipCode = ufm.getUserInfo(self.member, "zip")
        
        # Update zip
        if zipCode == "error":
            return await self.bot.say("Sorry, you're not in my file!")
        else:
            ufm.updateUserInfo(self.member, "zip", zipCode)

        # Load wunderAPI info into s and decode to d
        self.d = requests.get(Weather.wunderZipURL.format(Weather.wunderKey, zipCode)).json()
        
        # Except KeyError --> city isn't found 
        try:
            self.city = self.d["location"]["city"]
        except KeyError:
            return await self.bot.say("Sorry, I can't find you :(")

        # Store the relevant parts of the call in strings
        self.state = self.d["location"]["state"]
        self.temp = self.d["current_observation"]["temp_f"]
        self.conditions = self.d["current_observation"]["weather"]
        self.wind = self.d["current_observation"]["wind_string"]
        self.humidity = self.d["current_observation"]["relative_humidity"]

        return await self.bot.say("The weather for `{}, {}`: \n`{}` at `{}°F`. Winds `{}`. Relative humidity `{}`.".format(self.city, self.state, self.conditions, self.temp, self.wind.lower(), self.humidity))

    # Gets forecast based on zip
    @commands.bot.command(pass_context = True)
    async def fc(self, ctx, zipCode = ""):
        """ search via zip code """ 
        # Set cache expiry time
        requests_cache.install_cache(expire_after=3600)

        # user's snowflake ID
        self.member = str(ctx.message.author)   
        
        # Inits userfile if not found with given values
        if not ufm.foundUserFile():
            ufm.createUserFile(self.member, "zip", zipCode)

        # If value isn't entered, check zip against database
        if zipCode == "":
            zipCode = ufm.getUserInfo(self.member, "zip")
        
        # Find / update zip
        if zipCode == "error":
            return await self.bot.say("Sorry, you're not in my file!")
        else:
            ufm.updateUserInfo(self.member, "zip", zipCode)

        # json response in string form
        self.s = requests.get(Weather.wunderZipURL.format(Weather.wunderKey, zipCode)).text

        # Wunderground server overload handling
        try:
            self.d = json.loads(self.s)
        except ValueError:
            return await self.bot.say("Sorry, there is an issue with the Wunderground API")
        
        # Handling city not found error
        try:
            self.city = self.d["location"]["city"]
        except KeyError:
            return await self.bot.say("Sorry, I can't find you :(\n City: {}".format(city))
        
        # Load forecasts into strings
        self.foreTom = self.d["forecast"]["txt_forecast"]["forecastday"][2]["fcttext"]
        self.foreTomNight = self.d["forecast"]["txt_forecast"]["forecastday"][3]["fcttext"]

        return await self.bot.say("Tomorrow: `{0}`\nTomorrow Evening: `{1}`".format(self.foreTom, self.foreTomNight))

def setup(bot):
    bot.add_cog(Weather(bot))