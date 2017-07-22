import discord
import json
import requests
import requests_cache
from cogs.utils import DictManip as dm
from discord.ext import commands
from pathlib import Path


class OSRS():
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

        jsonItemData = requests.get(
            "https://raw.githubusercontent.com/Naughtsee/RS/master/item-data.json").json()
        print("Requesting json file from Github...")

        fstr = json.dumps(jsonItemData)
        print("Writing file...")

        data.write(fstr)
        print("Write complete")
        data.close()

    # Get GE Prices
    @commands.bot.command(name="ge")
    async def ge_search(self, *args):
        """ Get the buying/selling price and quantity of an OSRS item """
        # relevant API calls & formatted
        with open("data/item-data.json", "r") as f:
            item_data = json.load(f)

        types = ["buying", "selling", "buyingQuantity", "sellingQuantity"]
        typesf = ["Buying Price", "Selling Price",
                  "Buying Quantity", "Selling Quantity"]

        # Set cache expiry time
        requests_cache.install_cache(expire_after=300)

        # Condense the item into a string I can actually use
        # All items in DB are lowercase
        item = " ".join(args).lower()

        # Load json file & get price
        url = "https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}"
        try:
            json_dict = requests.get(
                (url.format(item_data[item]["id"]))).json()
        except:
            item = dm.getClosest(item_data, item)
            json_dict = requests.get(
                (url.format(item_data[item]["id"]))).json()

        # pretty print to discord
        return await self.bot.say("Current data for: `{}`\n{}: `{}`\n{}: `{}`\n{}: `{}`\n{}: `{}`".format(
            item,
            typesf[0], json_dict[types[0]],
            typesf[1], json_dict[types[1]],
            typesf[2], json_dict[types[2]],
            typesf[3], json_dict[types[3]]))


def setup(bot):
    bot.add_cog(OSRS(bot))
