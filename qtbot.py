#!/bin/env python

import discord
import json
import aiohttp
import aredis
from datetime import datetime
from discord.ext import commands

# Init bot
des = 'qtbot is a big qt written in python3 and love.'
bot = commands.Bot(command_prefix='.', description=des, pm_help=True)

# Get bot's token
with open('data/apikeys.json') as f:
    discord_bot_token = json.load(f)['discord']

# Create bot aiohttp session
bot.aio_session = aiohttp.ClientSession

# Create bot redis client
bot.redis_client = aredis.StrictRedis(host='localhost')

# Choose default cogs
bot.startup_extensions = (
    'cogs.admin',
    'cogs.generic',
    'cogs.weather',
    'cogs.comics',
    'cogs.dictionary',
    'cogs.osrs',
    'cogs.tmdb',
    'cogs.gif',
    'cogs.calc',
    'cogs.league',
    'cogs.ask',
    'cogs.meme',
    'cogs.error',
    'cogs.timer',
    'cogs.yt',
    'cogs.news',
    'cogs.wiki',
    'cogs.isup')

# Get current time for uptime
startTime = datetime.now()
startTimeStr = startTime.strftime('%B %d %H:%M:%S')

@bot.event
async def on_ready():
    """ Basic information printed via stdout """
    print('Client logged in at {}'.format(startTimeStr))
    print(bot.user.name)
    print(bot.user.id)
    print('------')

@bot.command(aliases=['up'])
async def uptime(ctx):
    """ Get current bot uptime """
    currentTime = datetime.now()
    currentTimeStr = currentTime.strftime('%B %d %H:%M:%S')

    await ctx.send('Initialized: `{}`\nCurrent Time: `{}`\nUptime: `{}`'.format(
    startTimeStr, currentTimeStr, str(currentTime - startTime).split('.')[0]))


if __name__ == '__main__':
    for ext in bot.startup_extensions:
        try:
            bot.load_extension(ext)
        except Exception as e:
            exc = '{}: {}'.format(type(e).__name__, e)
            print('failed to load extension {}\n{}'.format(ext, exc))

    bot.run(discord_bot_token)
