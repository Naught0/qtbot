import json
from typing import Union

import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw
from utils import dict_manip as dm
from utils.user_funcs import PGDB


class OSRS:
    def __init__(self, bot):
        self.bot = bot
        self.db = PGDB(bot.pg_con)
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.items_uri = 'https://rsbuddy.com/exchange/names.json'
        self.api_uri = 'https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}'
        self.player_uri = 'http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player={}'
        self.player_click_uri = 'http://services.runescape.com/m=hiscore_oldschool/hiscorepersonal.ws?user1={}'
        self.skills = ['Overall', 'Attack', 'Defense', 'Strength', 'Hitpoints', 'Ranged', 'Prayer',
                       'Magic', 'Cooking', 'Woodcutting', 'Fletching', 'Fishing', 'Firemaking',
                       'Crafting', 'Smithing', 'Mining', 'Herblore', 'Agility', 'Thieving', 'Slayer',
                       'Farming', 'Runecrafting', 'Hunter', 'Construction', 'Clue (Easy)', 'Clue (Medium)',
                       'Clue (All)', 'Bounty Hunter: Rogue', 'Bounty Hunter: Hunter', 'Clue (Hard)', 'LMS',
                       'Clue (Elite)', 'Clue (Master)']
        self.user_missing = 'Please either add a username or supply one.'
        self.user_not_exist = "Couldn't find a user matching {}"
        self.color = discord.Color.dark_gold()

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
        em = discord.Embed(title=item.title(), color=self.color)
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
                           color=self.color)
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

    @staticmethod
    def get_level(stat: str) -> int:
        """Helps parse player level from strings that look like 0,0,0"""
        return int(stat.split(',')[1])

    def calc_combat(self, user_info: dict) -> str:
        """Helper method which returns the player's combat level
        Formula here: http://oldschoolrunescape.wikia.com/wiki/Combat_level"""
        at = self.get_level(user_info['Attack'])
        st = self.get_level(user_info['Strength'])
        de = self.get_level(user_info['Defense'])
        hp = self.get_level(user_info['Hitpoints'])
        rn = self.get_level(user_info['Ranged'])
        mg = self.get_level(user_info['Magic'])
        pr = self.get_level(user_info['Prayer'])

        base = 0.25 * (de + hp + (pr // 2))
        melee = 0.325 * (at + st)
        range = 0.325 * ((rn // 2) + rn)
        mage = 0.325 * ((mg // 2) + mg)

        return str(int(base + max(melee, range, mage)))

    async def get_user_info(self, username: str) -> Union[dict, None]:
        """Helper method to see whether a user exists, if so, retrieves the data and formats it in a dict
        returns None otherwise"""
        user_info = await aw.aio_get_text(self.aio_session, self.player_uri.format(username))
        if user_info is None:
            return None

        # Player data is returned like so:
        # Rank, Level, XP
        # For clues, LMS, and Bounty Hunter it's:
        # Rank, Score
        # -1's denote no rank or xp
        return dict(zip(self.skills, user_info.split()))

    @commands.group(name='osrs', aliases=['hiscores', 'hiscore'], invoke_without_command=True)
    async def _osrs(self, ctx, *, username: str = None):
        """Get information about your OSRS stats"""
        image = None
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, 'osrs_name')
            image = await self.db.fetch_user_info(ctx.author.id, 'osrs_pic')

            # No users found
            if not username:
                return await ctx.error(self.user_missing)

        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        em = discord.Embed(title=f':bar_chart: {username}',
                           url=self.player_click_uri.format(username),
                           color=self.color)
        # See get_user_info for why things are wonky and split like this
        em.add_field(name='Combat Level', value=self.calc_combat(user_info), inline=False)
        em.add_field(name='Total Level', value=f"{int(user_info['Overall'].split(',')[1]):,}")
        em.add_field(name='Overall Rank', value=f"{int(user_info['Overall'].split(',')[0]):,}")

        if image:
            em.set_image(url=image)

        await ctx.send(embed=em)

    @_osrs.command()
    async def user(self, ctx, *, username: str):
        """Save your OSRS username so that you don't have supply it later"""
        await self.db.insert_user_info(ctx.author.id, 'osrs_name', username)
        await ctx.success(f'Added {username} ({ctx.author.display_name}) to database!')

    @_osrs.command()
    async def rmuser(self, ctx):
        """Remove your OSRS username from the database"""
        await self.db.remove_user_info(ctx.author.id, 'osrs_name')
        await ctx.success(f'Removed username from the database.')

    @_osrs.command(aliases=['avatar', 'pic'])
    async def picture(self, ctx, *, url: str):
        """Add a custom picture of your OSRS character to appear in the osrs command"""
        await self.db.insert_user_info(ctx.author.id, 'osrs_pic', url)
        await ctx.success(f'Added picture successfully')

    @_osrs.command(aliases=['rmavatar', 'rmpic'])
    async def rmpicture(self, ctx):
        """Remove your custom OSRS picture from the database"""
        await self.db.remove_user_info(ctx.author.id, 'osrs_pic')
        await ctx.success(f'Removed picture.')

    @_osrs.command(aliases=['clues', 'clu', 'clue scroll', 'cluescroll', 'cluescrolls'])
    async def clue(self, ctx, *, username: str = None):
        """Get your clue scroll ranks"""
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, 'osrs_name')
            if not username:
                return await ctx.error(self.user_missing)

        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        em = discord.Embed(title=f":scroll: {username}'s clues",
                           url=self.player_click_uri.format(username),
                           color=self.color)

        for item in user_info:
            if {'clue'} & set(item.lower().split()):
                v = user_info[item].split(',')
                # Handle no rank
                if v == ['-1', '-1']:
                    v = ['n/a', '0']
                    em.add_field(name=item, value=f'Rank: {v[0]} ({v[1]} clues)')
                # Cast to int for str formatting otherwise
                else:
                    v = [int(x) for x in v]
                    em.add_field(name=item, value=f'Rank: {v[0]:,} ({v[1]:,} clues)')

        # Now to swap Clue (All) to the first field
        overall = em._fields.pop(2)
        em._fields.insert(0, overall)

        await ctx.send(embed=em)

    @_osrs.command(aliases=['cb'])
    async def combat(self, ctx, *, username: str = None):
        """Check the combat stats of yourself or someone else"""
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, 'osrs_name')
            if not username:
                return await ctx.error(self.user_missing)

        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist)

        em = discord.Embed(title=f":right_facing_fist::left_facing_fist: {username}'s Combat Stats",
                           url=self.player_click_uri.format(username),
                           color=self.color)
        col1 = [f':crossed_swords: Combat {self.calc_combat(user_info)}',
                f':heart: Hitpoints {self.get_level(user_info["Hitpoints"])}',
                f':dagger: Attack {self.get_level(user_info["Attack"])}',
                f':fist: Strength {self.get_level(user_info["Attack"])}']
        col2 = [f':shield: Defence {self.get_level(user_info["Defense"])}',
                f':bow_and_arrow: Range {self.get_level(user_info["Ranged"])}',
                f':sparkles: Magic {self.get_level(user_info["Magic"])}',
                f':pray: Prayer {self.get_level(user_info["Prayer"])}']
        col1 = [f'{x:>15}' for x in col1]
        col2 = [f'{x:>13}' for x in col2]
        em.add_field(name='\u200B', value='\n'.join(col1))
        em.add_field(name='\u200B', value='\n'.join(col2))

        # em.add_field(name=':heart: Hitpoints', value=str(self.get_level(user_info['Hitpoints'])))
        # em.add_field(name=':crossed_swords: Attack', value=str(self.get_level(user_info['Attack'])))
        # em.add_field(name=':fist: Strength', value=str(self.get_level(user_info['Strength'])))
        # em.add_field(name=':shield: Defence', value=str(self.get_level(user_info['Defense'])))
        # em.add_field(name=':bow_and_arrow: Range', value=str(self.get_level(user_info['Ranged'])))
        # em.add_field(name=':sparkles: Magic', value=str(self.get_level(user_info['Magic'])))
        # em.add_field(name=':pray: Prayer', value=str(self.get_level(user_info['Prayer'])))

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(OSRS(bot))
