import discord
import json
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw
from discord.ext import commands
from utils.user_funcs import PGDB


class Weather:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.db = PGDB(bot.pg_con)
        self.cache_ttl = 3600
        self.url = 'http://bing.com/search'
        # Oh uh, this will make more sense later
        self.states = {'AK', 'AL', 'AR', 'AZ', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'IA', 'ID', 'IL', 'IN', 'KS',
                       'KY', 'LA', 'MA', 'MD', 'ME', 'MI', 'MN', 'MO', 'MS', 'MT', 'NC', 'ND', 'NE', 'NH', 'NJ', 'NM',
                       'NV', 'NY', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VA', 'VT', 'WA', 'WI',
                       'WV', 'WY'}
        # These are some old IE headers that give an easier page to scrape
        self.headers = {'User-Agent': 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0; GTB6.5; SLCC2; '
                                      '.NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0;'
                                      ' .NET4.0C; TheWorld)'}

    @staticmethod
    def f2c(weather_data: dict) -> dict:
        """ Converts F to C and returns the dict anew """
        # Celsius conversion
        weather_data['weather']['temp'] = int((weather_data['weather']['temp'] - 32) * (5 / 9))
        # MPH -> M/s
        weather_data['weather']['wind'] = int(weather_data['weather']['wind'] * 0.44704)

        return weather_data

    def get_weather_json(self, html: str) -> dict:
        """ Returns a dict representation of Bing weather """ 
        soup = BeautifulSoup(html, 'lxml')
        data = {
                   'weather': {
                       'loc': soup.find('div', class_='wtr_locTitle').text,
                       'temp': int(soup.find('div', class_='wtr_currTemp').text),
                       'precip': soup.find('div', class_='wtr_currPerci').text.split(': ')[-1],
                       'img_url': soup.find('img', class_='wtr_currImg')['src'],
                       'curr_cond': soup.find('div', class_='wtr_caption').text,
                       'wind': int(soup.find('div', class_='wtr_currWind').text.split(': ')[-1].split(' ')[0]),
                       'humidity': soup.find('div', class_='wtr_currHumi').text.split(': ')[-1] },

                   'forecast': [x['aria-label'] for x in soup.find_all('div', class_='wtr_forecastDay')]
        }
        data['needs_conversion'] = False if self.states & set(data['weather']['loc'].split(' ')) else True

        return data

    @commands.command(aliases=['az', 'al'])
    async def add_location(self, ctx, location: str):
        """ Add your location (zip, city, etc) to qtbot's database so 
        you don't have to supply it later """
        await self.db.insert_user_info(ctx.author.id, 'zipcode', location)
        await ctx.send(f'Successfully added location `{location}`.')

    @commands.command(aliases=['rz', 'rl'])
    async def remove_location(self, ctx):
        """ Remove your location from the database """
        await self.db.remove_user_info(ctx.author.id, 'zipcode')
        await ctx.send(f'Successfully removed location for `{ctx.author}`.')
    
    @commands.command(aliases=['wt'])
    async def weather(self, ctx, *, location: str = None):
        """ Get the weather of a given area (zipcode, city, etc.) """
        if location is None:
            location = await self.db.fetch_user_info(ctx.author.id, 'zipcode')
            if location is None:
                return await ctx.send("Sorry, you don't have a location saved.\n"
                                      "Feel free to use `al` to add your location, or supply one to the command")
        
        redis_key = f'{location}:weather'
        if await self.redis_client.exists(redis_key):
            raw_weather_str = await self.redis_client.get(redis_key)
            weather_data = json.loads(raw_weather_str)
        else:
            resp = await aw.aio_get_text(self.aio_session, self.url, headers=self.headers,
                                         params={'q': f'weather {location}'})
            weather_data = self.get_weather_json(resp)

            await self.redis_client.set(redis_key, json.dumps(weather_data), ex=self.cache_ttl)

        # Make SI conversions if needed
        if weather_data['needs_conversion']:
            celsius = True
            weather_data = self.f2c(weather_data)
        else:
            celsius = False

        c_wt = weather_data['weather']
        # Create the embed
        em = discord.Embed(title=c_wt['loc'])
        em.add_field(name='Temperature',
                     value=f"{c_wt['temp']}°F" if not celsius else f"{c_wt['temp']}°C")
        em.add_field(name='Conditions', value=c_wt['curr_cond'])
        em.add_field(name='Wind',
                     value=f"{c_wt['wind']} MPH" if not celsius else f"{c_wt['wind']} m/s")
        em.add_field(name='Chance of precipitation', value=c_wt['precip'])
        em.add_field(name='Humidity', value=c_wt['humidity'])
        em.set_thumbnail(url=c_wt['img_url'])

        await ctx.send(embed=em)


    @commands.command(aliases=['fc'])
    async def forecast(self, ctx, location: str = None):
        """ Get the forecast of a given location """
        if location is None:
            location = await self.db.fetch_user_info(ctx.author.id, 'zipcode')
            if location is None:
                return await ctx.send("Sorry, you don't have a location saved.\n"
                                      "Feel free to use `al` to add your location, or supply one to the command")

        redis_key = f'{location}:weather'
        if await self.redis_client.exists(redis_key):
            raw_weather_str = await self.redis_client.get(redis_key)
            weather_data = json.loads(raw_weather_str)
        else:
            resp = await aw.aio_get_text(self.aio_session, self.url, headers=self.headers,
                                         params={'q': f'weather {location}'})
            weather_data = self.get_weather_json(resp)

            await self.redis_client.set(redis_key, json.dumps(weather_data), ex=self.cache_ttl)

        await ctx.send('\n'.join(weather_data['forecast'][:2]))


def setup(bot):
    bot.add_cog(Weather(bot))
