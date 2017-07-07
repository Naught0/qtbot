import discord
import json
from datetime import datetime
from discord.ext import commands

# Init bot
des = "qtbot is a big qt written in python3 and _love_"
bot = commands.Bot(command_prefix=".", description=des)

# Get bot's token
with open("data/apikeys.json", "r") as f:
    apiKeys = json.load(f)
f.close()
discord_bot_token = apiKeys["discord"]

# Choose default cogs
startup_extensions = [
    "cogs.generic",
    "cogs.weather",
    "cogs.comics",
    "cogs.dictionary",
    "cogs.osrs",
    "cogs.movies",
    "cogs.gif",
    "cogs.calc",
    "cogs.league",
    "cogs.google",
    "cogs.yt"]

# Get current time for uptime
startTime = datetime.now()
startTimeStr = startTime.strftime("%B %d %H:%M:%S")

# Basic information printed via stdout


@bot.event
async def on_ready():
    print("Client logged in at {}".format(startTimeStr))
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def load(extension_name: str):
    """ Loads an extension """
    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        return await bot.say("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
    await bot.say("Cog `{}` loaded successfully.".format(extension_name))


@bot.command()
async def unload(extension_name: str):
    """ Unloads an extension. """
    bot.unload_extension(extension_name)
    return await bot.say("Cog `{}` has been unloaded.".format(extension_name))


@bot.command()
async def reload(extension_name: str):
    """ Reloads an extension """
    bot.unload_extension(extension_name)
    bot.load_extension(extension_name)
    return await bot.say("Cog `{}` has been reloaded.".format(extension_name))


@bot.command()
async def uptime():
    """ Get current uptime """
    currentTime = datetime.now()
    currentTimeStr = currentTime.strftime("%B %d %H:%M:%S")
    return await bot.say("Initialized: `{}`\nCurrent Time: `{}`\nUptime: `{}`".format(startTimeStr, currentTimeStr, str(currentTime - startTime).split(".")[0]))

if __name__ == "__main__":
    for ext in startup_extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("failed to load extension {}\n{}".format(ext, exc))

    bot.run(discord_bot_token)
