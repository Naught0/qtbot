import json
from urllib.parse import quote_plus
from typing import Union

import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw
from utils import dict_manip as dm
from utils.user_funcs import PGDB


class OSRS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = PGDB(bot.pg_con)
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client

        self.items_uri = "https://rsbuddy.com/exchange/names.json"
        # self.api_uri = 'https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}'
        self.prices_uri = "https://storage.googleapis.com/osb-exchange/summary.json"

        self.player_uri = (
            "http://services.runescape.com/m=hiscore_oldschool/index_lite.ws?player={}"
        )
        self.player_click_uri = "http://services.runescape.com/m=hiscore_oldschool/hiscorepersonal.ws?user1={}"
        self.skills = [
            "Overall",
            "Attack",
            "Defense",
            "Strength",
            "Hitpoints",
            "Ranged",
            "Prayer",
            "Magic",
            "Cooking",
            "Woodcutting",
            "Fletching",
            "Fishing",
            "Firemaking",
            "Crafting",
            "Smithing",
            "Mining",
            "Herblore",
            "Agility",
            "Thieving",
            "Slayer",
            "Farming",
            "Runecrafting",
            "Hunter",
            "Construction",
            "Clue (Easy)",
            "Clue (Medium)",
            "Clue (All)",
            "Bounty Hunter: Rogue",
            "Bounty Hunter: Hunter",
            "Clue (Hard)",
            "LMS",
            "Clue (Elite)",
            "Clue (Master)",
        ]
        self.statmoji = {
            "attack": ":dagger:",
            "strength": ":fist:",
            "defense": ":shield:",
            "ranged": ":bow_and_arrow:",
            "prayer": ":pray:",
            "magic": ":sparkles:",
            "runecrafting": ":crystal_ball:",
            "construction": ":house:",
            "hitpoints": ":heart:",
            "agility": ":runner:",
            "herblore": ":herb:",
            "thieving": ":spy:",
            "crafting": ":hammer_pick:",
            "fletching": ":cupid:",
            "slayer": ":skull_crossbones:",
            "hunter": ":feet:",
            "mining": ":pick:",
            "fishing": ":fish:",
            "cooking": ":cooking:",
            "firemaking": ":fire:",
            "woodcutting": ":deciduous_tree:",
            "farming": ":corn:",
        }

        self.user_missing = "Please either add a username or supply one."
        self.user_not_exist = "Couldn't find a user matching {}"
        self.color = discord.Color.dark_gold()

        with open("data/item-data.json") as f:
            self.item_data = json.load(f)

    @staticmethod
    def get_level(stat: str) -> int:
        """Helps parse player level from strings that look like 0,0,0"""
        return int(stat.split(",")[1])

    def calc_combat(self, user_info: dict) -> str:
        """Helper method which returns the player's combat level
        Formula here: http://oldschoolrunescape.wikia.com/wiki/Combat_level"""
        at = self.get_level(user_info["Attack"])
        st = self.get_level(user_info["Strength"])
        de = self.get_level(user_info["Defense"])
        hp = self.get_level(user_info["Hitpoints"])
        rn = self.get_level(user_info["Ranged"])
        mg = self.get_level(user_info["Magic"])
        pr = self.get_level(user_info["Prayer"])

        base = 0.25 * (de + hp + (pr // 2))
        melee = 0.325 * (at + st)
        range = 0.325 * ((rn // 2) + rn)
        mage = 0.325 * ((mg // 2) + mg)

        return str(int(base + max(melee, range, mage)))

    async def get_user_info(self, username: str) -> Union[dict, None]:
        """Helper method to see whether a user exists, if so, retrieves the data and formats it in a dict
        returns None otherwise"""
        user_info = await aw.aio_get_text(
            self.aio_session, self.player_uri.format(quote_plus(username))
        )
        if user_info is None:
            return None

        # Player data is returned like so:
        # Rank, Level, XP
        # For clues, LMS, and Bounty Hunter it's:
        # Rank, Score
        # -1's denote no rank or xp
        return dict(zip(self.skills, user_info.split()))

    @commands.group(
        name="osrs", aliases=["hiscores", "hiscore", "rs"], invoke_without_command=True
    )
    async def _osrs(self, ctx, *, username: str = None):
        """Get information about your OSRS stats"""
        image = None
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, "osrs_name")
            image = await self.db.fetch_user_info(ctx.author.id, "osrs_pic")

            # No users found
            if not username:
                return await ctx.error(self.user_missing)

        # User doesn't exist
        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        # Create embed
        em = discord.Embed(
            title=f":bar_chart: {username}",
            url=self.player_click_uri.format(quote_plus(username)),
            color=self.color,
        )
        # See get_user_info for why things are wonky and split like this
        overall = user_info["Overall"].split(",")
        em.add_field(
            name="Combat Level", value=self.calc_combat(user_info), inline=False
        )
        em.add_field(name="Total Level", value=f"{int(overall[1]):,}")
        em.add_field(name="Overall Rank", value=f"{int(overall[0]):,}")

        # Set image if one exists & if the player == the author
        if image:
            em.set_image(url=image)

        await ctx.send(embed=em)

    @_osrs.command()
    async def user(self, ctx, *, username: str):
        """Save your OSRS username so that you don't have to supply it later"""
        await self.db.insert_user_info(ctx.author.id, "osrs_name", username)
        await ctx.success(f"Added {username} ({ctx.author.display_name}) to database!")

    @_osrs.command()
    async def rmuser(self, ctx):
        """Remove your OSRS username from the database"""
        await self.db.remove_user_info(ctx.author.id, "osrs_name")
        await ctx.success(f"Removed username from the database.")

    @_osrs.command(aliases=["avatar", "pic"])
    async def picture(self, ctx, *, url: str):
        """Add a custom picture of your OSRS character to appear in the osrs command
        (Only when called by you)"""
        await self.db.insert_user_info(ctx.author.id, "osrs_pic", url)
        await ctx.success(f"Added picture successfully")

    @_osrs.command(aliases=["rmavatar", "rmpic"])
    async def rmpicture(self, ctx):
        """Remove your custom OSRS picture from the database"""
        await self.db.remove_user_info(ctx.author.id, "osrs_pic")
        await ctx.success(f"Removed picture.")

    @_osrs.command(aliases=["clues", "clu", "cluescroll", "cluescrolls"])
    async def clue(self, ctx, *, username: str = None):
        """Get your clue scroll counts & ranks"""
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, "osrs_name")
            if not username:
                return await ctx.error(self.user_missing)

        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        em = discord.Embed(
            title=f":scroll: {username}'s clues",
            url=self.player_click_uri.format(quote_plus(username)),
            color=self.color,
        )

        for item in user_info:
            if {"clue"} & set(item.lower().split()):
                v = user_info[item].split(",")
                # Handle no rank
                if v == ["-1", "-1"]:
                    v = ["n/a", "0"]
                    em.add_field(name=item, value=f"Rank: {v[0]} ({v[1]} clues)")
                # Cast to int for str formatting otherwise
                else:
                    v = [int(x) for x in v]
                    em.add_field(name=item, value=f"Rank: {v[0]:,} ({v[1]:,} clues)")

        # Now to swap Clue (All) to the first field
        overall = em._fields.pop(2)
        em._fields.insert(0, overall)

        await ctx.send(embed=em)

    @_osrs.command(aliases=["cb"])
    async def combat(self, ctx, *, username: str = None):
        """Check the combat stats of yourself or someone else"""
        if username is None:
            username = await self.db.fetch_user_info(ctx.author.id, "osrs_name")
            if not username:
                return await ctx.error(self.user_missing)

        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        em = discord.Embed(
            title=f":right_facing_fist::left_facing_fist: {username}'s Combat Stats",
            url=self.player_click_uri.format(quote_plus(username)),
            color=self.color,
        )
        col1 = [
            f":crossed_swords: Combat `{self.calc_combat(user_info)}`",
            f':heart: Hitpoints `{self.get_level(user_info["Hitpoints"])}`',
            f':dagger: Attack `{self.get_level(user_info["Attack"])}`',
            f':fist: Strength `{self.get_level(user_info["Strength"])}`',
        ]
        col2 = [
            f':shield: Defence `{self.get_level(user_info["Defense"])}`',
            f':bow_and_arrow: Range `{self.get_level(user_info["Ranged"])}`',
            f':sparkles: Magic `{self.get_level(user_info["Magic"])}`',
            f':pray: Prayer `{self.get_level(user_info["Prayer"])}`',
        ]
        em.add_field(name="\u200B", value="\n".join(col1))
        em.add_field(name="\u200B", value="\n".join(col2))

        await ctx.send(embed=em)

    @_osrs.command(aliases=["stats"])
    async def stat(self, ctx, username: str, stat_name: str):
        """Get a specific stat for a user
        Note:
        Be sure to wrap the username in quotation marks if it has spaces
        Username is required here per the limitations of Discord, sorry"""
        user_info = await self.get_user_info(username)
        if user_info is None:
            return await ctx.error(self.user_not_exist.format(username))

        # If input doesn't match exactly
        # Hopefully this handles common abbreviations (but I'm nearly sure it won't)
        if stat_name.lower() not in self.statmoji:
            stat_name = dm.get_closest(self.statmoji, stat_name)

        em = discord.Embed(
            title=f"{self.statmoji[stat_name.lower()]} {stat_name.title()} - {username}",
            url=self.player_click_uri.format(quote_plus(username)),
            color=self.color,
        )

        labels = ["Rank", "Level", "XP"]
        stat_list = user_info[stat_name.title()].split(",")
        for idx, label in enumerate(labels):
            em.add_field(name=label, value=f"{int(stat_list[idx]):,}")

        await ctx.send(embed=em)

    @_osrs.command(name="ge", invoke_without_command=True)
    async def ge_search(self, ctx, *, query):
        """ Get the buying/selling price and quantity of an OSRS item """

        # All items in the JSON are lowercase
        item = query.lower()

        # Checks whether item in json file
        if item in self.item_data:
            item_id = self.item_data[item]["id"]
        # Uses closest match to said item if no exact match
        else:
            item = dm.get_closest(self.item_data, item)
            item_id = self.item_data[item]["id"]

        if await self.redis_client.exists("osrs_prices"):
            item_prices = json.loads((await self.redis_client.get("osrs_prices")))
        else:
            item_prices = await aw.aio_get_json(self.aio_session, self.prices_uri)

            if not item_prices:
                return await ctx.error(
                    "The RSBuddy API is dead yet again. Try again in a bit."
                )

            await self.redis_client.set(
                "osrs_prices", json.dumps(item_prices), ex=(5 * 60)
            )

        # Create pretty embed
        em = discord.Embed(title=item.capitalize(), color=self.color)
        em.url = f"https://rsbuddy.com/exchange?id={item_id}"
        em.set_thumbnail(
            url=f"https://services.runescape.com/m=itemdb_oldschool/obj_big.gif?id={item_id}"
        )
        em.add_field(
            name="Buying Price", value=f'{item_prices[item_id]["buy_average"]:,}gp'
        )
        em.add_field(
            name="Selling Price", value=f'{item_prices[item_id]["sell_average"]:,}gp'
        )
        em.add_field(
            name="Buying Quantity", value=f'{item_prices[item_id]["buy_quantity"]:,}/hr'
        )
        em.add_field(
            name="Selling Quantity",
            value=f'{item_prices[item_id]["sell_quantity"]:,}/hr',
        )

        await ctx.send(embed=em)

    @commands.command(name="geupdate")
    @commands.is_owner()
    async def _update(self, ctx):
        """A command to update the OSRS GE item list"""
        new_items = await aw.aio_get_json(self.aio_session, self.items_uri)

        # This 503's a lot, if not every time, not sure yet
        if new_items is None:
            em = discord.Embed(
                title=":no_entry_sign: RS buddy is serving up a 503!",
                color=discord.Color.dark_red(),
            )

            return await ctx.send(embed=em)

        if len(new_items) == len(self.item_data):
            em = discord.Embed(
                title=":no_entry_sign: Items already up-to-date boss!",
                color=discord.Color.dark_red(),
            )

            return await ctx.send(embed=em)

        filtered_items = {}
        for item in new_items:
            filtered_items[new_items[item]["name"].lower()] = {
                "id": item,
                "name": new_items[item]["name"],
            }

        with open("data/item-data.json", "w") as f:
            json.dump(filtered_items, f, indent=2)

        self.item_data = filtered_items

        num_updated = len(new_items) - len(self.item_data)
        await ctx.success(f"Updated `{num_updated}` item(s).")

        # The osbuddy api just 503s every time, keeping this commented in the hopes that it works in the future
        # em = discord.Embed(title=':white_check_mark: Check here',
        #                    url='https://rsbuddy.com/exchange/names.json',
        #                    color=self.color)
        # em.description = ("```py\n"
        #                   "data = requests.get('https://rsbuddy.com/exchange/names.json').json() d = {}\n\n"
        #                   "for item in data:\n"
        #                   "\td[data[item]['name'].lower()] = {'id': item, 'name': data[item]['name']}"
        #                   "```")

        # await ctx.send(embed=em)

def setup(bot):
    bot.add_cog(OSRS(bot))
