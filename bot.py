import json
import os
import traceback
from datetime import datetime
from pathlib import Path

import aiohttp
import asyncpg
import discord
from discord.ext import commands

from prisma import Prisma
from utils.cache import redis_client
from utils.custom_context import CustomContext


class QTBot(commands.Bot):
    prisma: Prisma

    def __init__(self, config_file, *args, **kwargs):
        self.config_file = config_file
        self.description = "qtbot is a big qt written in python3 and love."
        self.do_not_load = ("league", "covid", "poll", "music", "timer", "ris")

        with open(self.config_file) as f:
            self.api_keys = json.load(f)

        self.token = self.api_keys["discord"]
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=self.get_prefix,
            description=self.description,
            help_command=commands.DefaultHelpCommand(dm_help=True),
            case_insensitive=True,
            intents=intents,
            *args,
            **kwargs,
        )

        self.redis_client = redis_client
        self.startup_extensions = [x.stem for x in Path("cogs").glob("*.py")]
        self.add_check(self.block_bots)

    def run(self):
        super().run(self.token)

    async def setup_hook(self):
        await self.create_db_pool()
        await self.load_all_prefixes()
        db = Prisma()
        await db.connect()
        self.prisma = db
        self.aio_session = aiohttp.ClientSession()

        # Add the application command interaction check to filter slash commands if you use them
        self.tree.interaction_check = self.block_bot_interactions

        if not hasattr(self, "start_time"):
            self.start_time = datetime.now()
            self.start_time_str = self.start_time.strftime("%B %d %H:%M:%S")

        for extension in self.startup_extensions:
            if extension not in self.do_not_load:
                try:
                    await self.load_extension(f"cogs.{extension}")
                except Exception:
                    print(f"Failed Extension: {extension}")
                    traceback.print_exc()
                else:
                    print(f"Loaded Extension: {extension}")

        print(f"Client logged in at {self.start_time_str}")
        print(self.user.name)
        print(self.user.id)
        print("----------")

    async def load_all_prefixes(self):
        pres = await self.pg_con.fetch("SELECT * from custom_prefix")
        self.pre_dict = {r["guild_id"]: r["prefix"] for r in pres}

    async def get_prefix(self, message: discord.Message):
        try:
            return ("qt.", self.pre_dict[message.guild.id])
        except (KeyError, AttributeError):
            return "qt."

    async def create_db_pool(self):
        self.pg_con = await asyncpg.create_pool(os.getenv("DATABASE_URL"))

    async def block_bots(self, ctx: commands.Context) -> bool:
        return not ctx.author.bot

    async def block_bot_interactions(self, interaction: discord.Interaction) -> bool:
        return not interaction.user.bot

    async def on_message(self, message):
        if message.author.bot:
            return

        ctx = await self.get_context(message, cls=CustomContext)
        await self.invoke(ctx)
