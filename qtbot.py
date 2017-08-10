#!/bin/env python

import discord
import json
from datetime import datetime
from discord.ext import commands

# Init bot
des = "qtbot is a big qt written in python3 and love."
bot = commands.Bot(command_prefix=".", description=des, pm_help=True)

# Get bot's token
with open("data/apikeys.json", "r") as f:
    discord_bot_token = json.load(f)["discord"]

# Choose default cogs
startup_extensions = (
    "cogs.generic",
    "cogs.weather",
    "cogs.comics",
    "cogs.dictionary",
    "cogs.osrs",
    "cogs.tmdb",
    "cogs.gif",
    "cogs.calc",
    "cogs.league",
    "cogs.google",
    "cogs.yt",
    "cogs.news",
    "cogs.wiki",
    "cogs.isup")

# Default message to save me some typing for user is not owner
not_owner_message = "Sorry, you have to be supreme overlord to run this command."

# Get current time for uptime
startTime = datetime.now()
startTimeStr = startTime.strftime("%B %d %H:%M:%S")


@bot.event
async def on_ready():
    # Basic information printed via stdout
    print("Client logged in at {}".format(startTimeStr))
    print(bot.user.name)
    print(bot.user.id)
    print('------')


@bot.command()
async def load(ctx, extension_name: str):
    """ Loads an extension """
    if not bot.is_owner(ctx.author):
        await ctx.send(not_owner_message)

    try:
        bot.load_extension(extension_name)
    except (AttributeError, ImportError) as e:
        return await ctx.send("```py\n{}: {}\n```".format(type(e).__name__, str(e)))
    await ctx.send("Cog `{}` loaded successfully.".format(extension_name))


@bot.command()
async def unload(ctx, extension_name: str):
    """ Unloads an extension. """
    if not bot.is_owner(ctx.author):
        await ctx.send(not_owner_message)

    bot.unload_extension(extension_name)
    await ctx.send("Cog `{}` has been unloaded.".format(extension_name))


@bot.command(aliases="r")
async def reload(ctx, extension_name: str):
    """ Reloads an extension """
    if not bot.is_owner(ctx.author):
        await ctx.send(not_owner_message)

    bot.unload_extension(extension_name)
    bot.load_extension(extension_name)
    await ctx.send("Cog `{}` has been reloaded.".format(extension_name))


@bot.command(aliases=["up"])
async def uptime(ctx):
    """ Get current uptime """
    currentTime = datetime.now()
    currentTimeStr = currentTime.strftime("%B %d %H:%M:%S")
    await ctx.send("Initialized: `{}`\nCurrent Time: `{}`\nUptime: `{}`".format(startTimeStr, currentTimeStr, str(currentTime - startTime).split(".")[0]))

if __name__ == "__main__":
    for ext in startup_extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            exc = "{}: {}".format(type(e).__name__, e)
            print("failed to load extension {}\n{}".format(ext, exc))

    bot.run(discord_bot_token)
