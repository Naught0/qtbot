import os
import json
import traceback
from datetime import datetime
from pathlib import Path

import aiohttp
import aredis
from aredis.client import asyncio
import asyncpg
import discord
from discord.ext import commands

from utils.custom_context import CustomContext


class QTBot(commands.Bot):
    def __init__(self, config_file, *args, **kwargs):
        self.config_file = config_file
        self.description = "qtbot is a big qt written in python3 and love."
        self.do_not_load = ("league", "covid", "poll", "music", "timer", "ris")

        with open(self.config_file) as f:
            self.api_keys = json.load(f)

        self.token = self.api_keys["discord"]
        intents = discord.Intents.default()
        intents.members = True

        super().__init__(
            command_prefix=self.get_prefix,
            description=self.description,
            help_command=commands.DefaultHelpCommand(dm_help=True),
            case_insensitive=True,
            intents=intents,
            *args,
            **kwargs,
        )

        self.aio_session = aiohttp.ClientSession()
        # self.rune_client = lolrune.AioRuneClient()
        self.redis_client = aredis.StrictRedis(
            host=os.getenv("REDIS_HOST"), decode_responses=True
        )
        self.startup_extensions = [x.stem for x in Path("cogs").glob("*.py")]
        asyncio.run(self.create_db_pool())
        asyncio.run(self.load_all_prefixes())

    def run(self):
        super().run(self.token)

    async def load_all_prefixes(self):
        pres = await self.pg_con.fetch("SELECT * from custom_prefix")
        # Load custom prefixes into a dict
        self.pre_dict = {r["guild_id"]: r["prefix"] for r in pres}

    async def get_prefix(self, message):
        try:
            return ("qt.", self.pre_dict[message.guild.id])
        except (KeyError, AttributeError):
            return "qt."

    async def create_db_pool(self):
        self.pg_con = await asyncpg.create_pool(os.getenv("DATABASE_URL"))

    async def on_message(self, message):
        ctx = await self.get_context(message, cls=CustomContext)
        await self.invoke(ctx)

    async def on_ready(self):
        if not hasattr(self, "start_time"):
            self.start_time = datetime.now()
            self.start_time_str = self.start_time.strftime("%B %d %H:%M:%S")

        for extension in self.startup_extensions:
            if extension not in self.do_not_load:
                try:
                    self.load_extension(f"cogs.{extension}")
                except:
                    print(f"Failed Extension: {extension}")
                    traceback.print_exc()
                else:
                    print(f"Loaded Extension: {extension}")

        print(f"Client logged in at {self.start_time_str}")
        print(self.user.name)
        print(self.user.id)
        print("----------")
