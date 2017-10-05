import json
import aredis
import discord
import aiohttp
import asyncpg
import traceback
from datetime import datetime
from discord.ext import commands

class QTBot(commands.Bot):
    def __init__(self, config_file, *args, **kwargs):
        self.config_file = config_file
        self.description = 'qtbot is a big qt written in python3 and love.'
        
        with open(self.config_file) as f:
            self.token = json.load(f)['discord']

        super().__init__(command_prefix='.', description=self.description,
                         pm_help=True, *args, **kwargs)

        self.aio_session = aiohttp.ClientSession(loop=self.loop)
        self.redis_client = aredis.StrictRedis(host='localhost', decode_responses=True)


        self.startup_extensions = (
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
            'cogs.eval',
            'cogs.timer',
            'cogs.test',
            'cogs.tag',
            'cogs.yt',
            'cogs.news',
            'cogs.wiki',
            'cogs.isup',)

        self.loop.run_until_complete(self.create_db_pool())

    def run(self):
        super().run(self.token)

    async def create_db_pool(self):
        with open(self.config_file) as f:
            self.pg_pw = json.load(f)['postgres']
        self.pg_con = await asyncpg.create_pool(user='james', password=self.pg_pw,
                                                database='discord_testing')

    async def on_ready(self):
        if not hasattr(self, 'start_time'):
            self.start_time = datetime.now()
            self.start_time_str = self.start_time.strftime('%B %d %H:%M:%S')

        for extension in self.startup_extensions:
            try:
                self.load_extension(extension)
            except:
                print(f'Failed Extension: {extension}')
                traceback.print_exc()
            else:
                print(f'Loaded Extension: {extension}')

        print(f'Client logged in at {self.start_time_str}')
        print(self.user.name)
        print(self.user.id)
        print('----------')
