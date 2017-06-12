import discord, json, requests, requests_cache
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
        self.data = None
        print("Creating OSRS data file...")
        self.data = open("data/item-data.json", "w")
        print("Done")

        self.jsonItemData = requests.get("https://raw.githubusercontent.com/Naughtsee/RS/master/item-data.json").json()
        print("Requesting json file from Github...")

        self.fstr = json.dumps(jsonItemData)
        print("Writing file...")

        self.data.write(fstr)
        print("Write complete\nInitializing bot...\n------")
        self.data.close()

    # Get GE Prices
    @commands.bot.command(aliases = ['ge'])
    async def grandExchange(self, *args):
        """ Get the buying/selling price and quantity of an OSRS item """
        # relevant API calls & formatted    
        with open("data/item-data.json", "r") as f:
            self.item_data = json.load(f)
        
        self.types = ["buying", "selling", "buyingQuantity", "sellingQuantity"]
        self.typesf = ["Buying Price", "Selling Price", "Buying Quantity", "Selling Quantity"]

        # Set cache expiry time
        requests_cache.install_cache(expire_after = 300)
        
        # Condense the item into a string I can actually use
        # All items in DB are lowercase
        self.item = " ".join(args).lower()

        # Load json file & get price
        self.url = "https://api.rsbuddy.com/grandExchange?a=guidePrice&i={}"
        try:
            self.json_dict = requests.get((url.format(item_data[item]["id"]))).json()
        except:
            self.item = dm.getClosest(self.item_data, self.item) 
            self.json_dict = requests.get((self.url.format(self.item_data[self.item]["id"]))).json()
        
        # pretty print to discord
        return await self.bot.say("Current data for: `{}`\n{}: `{}`\n{}: `{}`\n{}: `{}`\n{}: `{}`".format(
            self.item,
            self.typesf[0], self.json_dict[self.types[0]], 
            self.typesf[1], self.json_dict[self.types[1]], 
            self.typesf[2], self.json_dict[self.types[2]], 
            self.typesf[3], self.json_dict[self.types[3]]))

def setup(bot):
    bot.add_cog(OSRS(bot))