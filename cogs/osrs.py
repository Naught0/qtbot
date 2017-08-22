import discord
import json
from utils import aiohttp_wrap as aw
from utils import dict_manip as dm
from discord.ext import commands
from pathlib import Path


class OSRS:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.api_uri = 'https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}'

    def check_osrs_json_file(ctx):
        return Path('data/item-data.json').is_file()

    @commands.command(name='ge', aliases=['exchange'])
    @commands.check(check_osrs_json_file)
    @commands.cooldown(rate=1, per=1.0, type=commands.BucketType.user)
    async def ge_search(self, ctx, *, query):
        """ Get the buying/selling price and quantity of an OSRS item """

        # Json item data
        with open('data/item-data.json') as f:
            item_data = json.load(f)

        # All items in DB are lowercase
        item = query.lower()

        # Checks whether item in json file
        if item in item_data:
            item_id = item_data[item]['id']
            item_pricing_dict = await aw.aio_get_json(self.aio_session, self.api_uri.format(item_id))

        # Uses closest match in edit distance if no matches
        else:
            item = dm.get_closest(item_data, item)
            item_id = item_data[item]['id']
            item_pricing_dict = await aw.aio_get_json(self.aio_session, self.api_uri.format(item_id))

        # Create pretty embed
        em = discord.Embed()
        em.color = discord.Colour.dark_gold()
        em.title = item.title()
        em.url = 'https://rsbuddy.com/exchange?id={}'.format(item_id)
        em.set_thumbnail(url='https://services.runescape.com/m=itemdb_oldschool/1502360694249_obj_big.gif?id={}'.format(item_id))
        em.add_field(name='Buying Price', value='{:,}gp'.format(item_pricing_dict['buying']))
        em.add_field(name='Selling Price', value='{:,}gp'.format(item_pricing_dict['selling']))
        em.add_field(name='Buying Quantity', value='{:,}/hr'.format(item_pricing_dict['buyingQuantity']))
        em.add_field(name='Selling Quantity', value='{:,}/hr'.format(item_pricing_dict['sellingQuantity']))

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(OSRS(bot))
