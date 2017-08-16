import discord
import json
import requests
import requests_cache
from cogs.utils import DictManip as dm
from discord.ext import commands
from pathlib import Path


class OSRS:
    def __init__(self, bot):
        self.bot = bot

    def check_osrs_json_file(ctx):
        return Path("data/item-data.json").is_file()

    # Get GE Prices
    @commands.command(name="ge", aliases=["exchange"])
    @commands.check(check_osrs_json_file)
    async def ge_search(self, ctx, *, query):
        """ Get the buying/selling price and quantity of an OSRS item """
        # relevant API calls & formatted
        with open("data/item-data.json") as f:
            item_data = json.load(f)

        # Set cache expiry time
        requests_cache.install_cache(expire_after=300)

        # All items in DB are lowercase
        item = query.lower()

        # Load json file & get price
        url = "https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}"

        # Spell correct to get the closest match on the item if not found immediately in the item_data
        if item in item_data:
            item_id = item_data[item]["id"]
            item_pricing_dict = requests.get(
                (url.format(item_id))).json()
        else:
            item = dm.getClosest(item_data, item)
            item_id = item_data[item]["id"]
            item_pricing_dict = requests.get(
                (url.format(item_id))).json()

        # Create pretty embed
        em = discord.Embed()
        em.color = discord.Colour.dark_gold()
        em.title = item.title()
        em.url = "https://rsbuddy.com/exchange?id={}".format(item_id)
        em.set_thumbnail(url="https://services.runescape.com/m=itemdb_oldschool/1502360694249_obj_big.gif?id={}".format(item_id))
        em.add_field(name="Buying Price", value="{:,}gp".format(item_pricing_dict["buying"]))
        em.add_field(name="Selling Price", value="{:,}gp".format(item_pricing_dict["selling"]))
        em.add_field(name="Buying Quantity", value="{:,}/hr".format(item_pricing_dict["buyingQuantity"]))
        em.add_field(name="Selling Quantity", value="{:,}/hr".format(item_pricing_dict["sellingQuantity"]))

        await ctx.send(embed=em)


def setup(bot):
    # if OSRS.item_file_exists:
    #     bot.add_cog(OSRS(bot))
    # else:
    #     print("Please download the item-data.json file from github to the data folder.")
    #     print("https://raw.githubusercontent.com/Naught0/qtbot/master/data/item-data.json")
    bot.add_cog(OSRS(bot))
