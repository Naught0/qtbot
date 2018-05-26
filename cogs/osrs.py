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
        self.player_uri = 'http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player={}'
        self.skills = ['Overall', 'Attack', 'Defense', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
                       'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking',
                       'Crafting', 'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
                       'Farming', 'Runecrafting', 'Hunter', 'Construction', 'Clue (Easy)', 'Clue (Medium)',
                       'Clue (All)', 'Bounty Hunter: Rogue', 'Bounty Hunter: Hunter', 'Clue (Hard)', 'LMS',
                       'Clue (Elite)', 'Clue (Master)']

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
                return await ctx.error('Couldn\'t contact the RSBuddy API, please try again later')

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
        em.description = \
            """
            ```py
            data = requests.get('https://rsbuddy.com/exchange/names.json').json()
            d = {}
            for item in data:
                d[data[item]['name'].lower()] = {'id': item, 'name': data[item]['name']}
            ```
            """

        await ctx.send(embed=em)

    @commands.command(name='osrs', aliases=['hiscores', 'hiscore'], invoke_without_command=True)
    async def _osrs(self, ctx, *, username):
        """Get information about your OSRS stats"""
        player_data = await aw.aio_get_text(self.aio_session, self.player_uri.format(username))
        if player_data is None:
            return await ctx.error(f'Couldn\'t find anyone named {username}.')

        stats = dict(zip(self.skills, player_data.split()))

        em = discord.Embed(color=discord.Color.dark_gold())
        em.set_author(name=username, icon_url='https://king4rs.com/31-large_default/novice-osrs-quest.jpg',
                      url=f'http://services.runescape.com/m=hiscore_oldschool/hiscorepersonal.ws?user1={username}')

        for field in stats:
            if field == 'Overall':
                em.add_field(name=field, value=stats[field].split(',')[1], inline=False)
                continue
            if 'clue' in field.lower():
                continue

            em.add_field(name=field, value=stats[field].split(',')[1])

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(OSRS(bot))
