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
        # Write item file for OSRS price query
        # If no file, make one
        if Path("data/item-data.json").is_file():
            print("Skipping json file download...\nReading file...\n------")
        else:
            data = None
            print("Creating OSRS data file...")
            data = open("data/item-data.json", "w")
            print("Done")

            item_data_json = requests.get(
                "https://raw.githubusercontent.com/Naughtsee/RS/master/item-data.json").json()
            print("Requesting json file from Github...")

            print("Writing file...")

            with open("data/item-data.json", "w") as f:
                json.dump(item_data_json, f)

            print("Write complete")

    # Get GE Prices
    @commands.command(name="ge", aliases=["exchange"])
    async def ge_search(self, ctx, *, query):
        """ Get the buying/selling price and quantity of an OSRS item """
        # relevant API calls & formatted
        with open("data/item-data.json") as f:
            item_data = json.load(f)

        types = ["buying", "selling", "buyingQuantity", "sellingQuantity"]
        typesf = ["Buying Price", "Selling Price",
                  "Buying Quantity", "Selling Quantity"]

        # Set cache expiry time
        requests_cache.install_cache(expire_after=300)

        # All items in DB are lowercase
        item = query.lower()

        # Load json file & get price
        url = "https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}"
        try:
            item_id = item_data[item]["id"]
            item_pricing_dict = requests.get(
                (url.format(item_id))).json()
        except:
            item = dm.getClosest(item_data, item)
            item_id = item_data[item]["id"]
            item_pricing_dict = requests.get(
                (url.format(item_id))).json()

        # Get item icon
        icon_url = "https://services.runescape.com/m=itemdb_oldschool/1502360694249_obj_big.gif?id={}".format(item_id)

        # Create pretty embed
        em = discord.Embed()
        em.title = item.title()
        em.url = "https://rsbuddy.com/exchange?id={}".format(item_id)
        em.set_thumbnail(url=icon_url)
        em.add_field(name="Buying Price", value="{:,}gp".format(item_pricing_dict["buying"]))
        em.add_field(name="Selling Price", value="{:,}gp".format(item_pricing_dict["selling"]))
        em.add_field(name="Buying Quantity", value="{:,}/hr".format(item_pricing_dict["buyingQuantity"]))
        em.add_field(name="Selling Quantity", value="{:,}/hr".format(item_pricing_dict["sellingQuantity"]))

        await ctx.send(embed=em)
        

def setup(bot):
    bot.add_cog(OSRS(bot))
