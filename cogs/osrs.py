import json

import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw
from utils import dict_manip as dm


class OSRS:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.items_uri = 'https://rsbuddy.com/exchange/names.json'
        self.api_uri = 'https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}'

        with open('data/item-data.json') as f:
            self.item_data = json.load(f)

    @commands.group(name='ge', invoke_without_command=True)
    async def ge_search(self, ctx, *, query):
        """ Get the buying/selling price and quantity of an OSRS item """

        # All items in the JSON are lowercase
        item = query.lower()

        # Checks whether item in json file
        if item in self.item_data:
            item_id = self.item_data[item]['id']
        # Uses closest match to said item if no exact match
        else:
            item = dm.get_closest(self.item_data, item)
            item_id = self.item_data[item]['id']

        # Check our handy-dandy redis cache
        if await self.redis_client.exists(f'osrs:{item_id}'):
            item_pricing_dict = await self.redis_client.get(f'osrs:{item_id}')
            item_pricing_dict = json.loads(item_pricing_dict)
        else:
            item_pricing_dict = await aw.aio_get_json(self.aio_session, self.api_uri.format(item_id))

            if not item_pricing_dict:
                return await ctx.send(
                    'Sorry, I was unable to communicate with the RSBuddy API. Please try again later.')

            await self.redis_client.set(f'osrs:{item_id}', json.dumps(item_pricing_dict), ex=(10 * 60))

        # Create pretty embed
        em = discord.Embed(title=item.title(), color=discord.Color.dark_gold())
        em.url = f'https://rsbuddy.com/exchange?id={item_id}'
        em.set_thumbnail(url=f'https://services.runescape.com/m=itemdb_oldschool/obj_big.gif?id={item_id}')
        em.add_field(name='Buying Price', value=f'{item_pricing_dict["buying"]:,}gp')
        em.add_field(name='Selling Price', value=f'{item_pricing_dict["selling"]:,}gp')
        em.add_field(name='Buying Quantity', value=f'{item_pricing_dict["buyingQuantity"]:,}/hr')
        em.add_field(name='Selling Quantity', value=f'{item_pricing_dict["sellingQuantity"]:,}/hr')

        await ctx.send(embed=em)

    @ge_search.command(name='update')
    @commands.is_owner()
    async def _update(self, ctx):
        """A command to update the OSRS GE item list"""
        # new_items = await aw.aio_get_json(self.aio_session, self.items_uri)
        #
        # # This 503's a lot, if not every time, not sure yet
        # if new_items is None:
        #     em = discord.Embed(title=':no_entry_sign: RS buddy is serving up a 503!',
        #                        color=discord.Color.dark_red())
        #
        #     return await ctx.send(embed=em)
        #
        # if len(new_items) == len(self.item_data):
        #     em = discord.Embed(title=':no_entry_sign: Items already up-to-date boss!',
        #                        color=discord.Color.dark_red())
        #
        #     return await ctx.send(embed=em)
        #
        # with open('data/item-data.json', 'w') as f:
        #     json.dump(new_items, f, indent=2)
        #
        # num_updated = len(new_items) - len(self.item_data)
        # em = discord.Embed(title=f':white_check_mark: {num_updated} Item(s) updated!',
        #                    color=discord.Color.dark_green())

        # The osbuddy api just 503s every time, keeping this up
        # in the hopes that this works in the future
        em = discord.Embed(title=':white_check_mark: Check here',
                           url='https://rsbuddy.com/exchange/names.json',
                           color=discord.Color.dark_gold())

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(OSRS(bot))
