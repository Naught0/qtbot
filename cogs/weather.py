import discord
import json
from utils import aiohttp_wrap as aw
from utils import user_funcs as ufm
from discord.ext import commands


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.weather_icon_dict = {'storm': 'https://ssl.gstatic.com/onebox/weather/128/thunderstorms.png', 'partly_cloudy': 'https://ssl.gstatic.com/onebox/weather/128/partly_cloudy.png', 'mostly_cloudy': 'https://ssl.gstatic.com/onebox/weather/128/cloudy.png', 'clear': 'https://ssl.gstatic.com/onebox/weather/128/sunny.png', 'rain': 'https://ssl.gstatic.com/onebox/weather/128/rain.png'}
        self.api_url = 'http://api.wunderground.com/api/{}/forecast/geolookup/conditions/q/{}.json'

        with open('data/apikeys.json') as f:
            self.self.api_key = json.load(f)['wunderground']

    @commands.command(name='az')
    async def add_zip(self, ctx, zip_code=None):
        """ Add your zipcode for qtbot to remember. """

        # No zipcode supplied
        if (zip_code is None):
            return await ctx.send('Please supply a zipcode.')

        # Invalid zip supplied
        if (len(zip_code) != 5 or not zip_code.isnumeric()):
            return await ctx.send('Please supply a valid zipcode.')

        # Get user ID
        member = str(ctx.author)

        # Add zipcode to file
        ufm.update_user_info(member, 'zip', zip_code)

        await ctx.send('Successfully added zipcode `{}` for user `{}`.'.format(zip_code, member))

    # Gets weather based on zip
    @commands.command(name='wt', aliases=['w'])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def weather(self, ctx, zip_code=''):
        """ Search with zipcode, or not, and qtbot will try to find your zip from the userfile. """

        member = str(ctx.author)

        # If no zipcode provided
        if zip_code == '':
            zip_code = ufm.get_user_info(member, 'zip')

        # get_user_info returns None if user has no zip on file
        if zip_code is None:
            return await ctx.send("Sorry, you're not in my file!\n Please `az` with a zipcode.")

        # Load wunderAPI info into d
        # Sometimes wunderground dies --> handle it
        try:
            d = aw.aio_get_json(self.aio_session, self.api_url.format(
                self.api_key, zip_code))
        except ConnectionError:
            return await ctx.send('Sorry, wunderground is having trouble with this request. Try again in a bit.')

        # Except KeyError --> city isn't found
        try:
            city = d['location']['city']
        except KeyError:
            return await ctx.send("Sorry, I'm having trouble finding your location.")

        # Store the relevant parts of the call in strings
        state = d['location']['state']
        temp = d['current_observation']['temp_f']
        conditions = d['current_observation']['weather']
        wind = d['current_observation']['wind_string']
        humidity = d['current_observation']['relative_humidity']

        # Create the embed
        em = discord.Embed()
        em.title = 'Weather for {}, {}'.format(city, state)
        em.add_field(name='Temperature', value='{}°F'.format(temp))
        em.add_field(name='Conditions', value=conditions)
        em.add_field(name='Relative humidity', value=humidity)
        em.add_field(name='Winds', value=wind)

        # Conditions to lower
        cond_lower = conditions.lower()
        if 'rain' in cond_lower:
            em.set_thumbnail(url=self.weather_icon_dict['rain'])
        elif 'clear' in cond_lower or 'sunny' in cond_lower:
            em.set_thumbnail(url=self.weather_icon_dict['clear'])
        elif 'partly' in cond_lower:
            em.set_thumbnail(url=self.weather_icon_dict['partly_cloudy'])
        elif 'cloudy' in cond_lower or 'overcast' in cond_lower:
            em.set_thumbnail(url=self.weather_icon_dict['mostly_cloudy'])
        elif 'storm' in cond_lower or 'thunderstorm' in cond_lower:
            em.set_thumbnail(url=self.weather_icon_dict['storm'])

        await ctx.send(embed=em)

    # Gets forecast based on zip
    @commands.command(name='fc', aliases=['f'])
    @commands.cooldown(rate=1, per=120.0, type=commands.BucketType.user)
    async def forecast(self, ctx, zip_code=''):
        """ Search with zipcode, or not, and qtbot will try to find your zip from the userfile."""

        # user's snowflake ID
        member = str(ctx.author)

        # If no zipcode provided
        if zip_code == '':  # Find zipcode in file
            zip_code = ufm.get_user_info(member, 'zip')

        # UFM returns str error if no zip found
        if zip_code is None:
            return await ctx.send("Sorry, you're not in my file!\nPlease use `az` with a valid zipcode.")

        # Json response in string form
        d = aw.aio_get_json(self.aio_session, self.api_url.format(
            self.api_key, zip_code))

        # Handling city not found error
        try:
            city = d['location']['city']
        except KeyError:
            return await ctx.send("Sorry, I'm having trouble finding your location.")

        # Load forecasts into strings
        foreTom = d['forecast']['txt_forecast']['forecastday'][2]['fcttext']
        foreTomNight = d['forecast']['txt_forecast']['forecastday'][3]['fcttext']

        await ctx.send('Tomorrow: `{}`\nTomorrow Evening: `{}`'.format(foreTom, foreTomNight))


def setup(bot):
    bot.add_cog(Weather(bot))
