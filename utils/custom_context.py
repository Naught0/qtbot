import discord
from discord.ext import commands

from bot import QTBot


class CustomContext(commands.Context):
    bot: QTBot

    async def error(self, title: str, description: str = None):
        em = discord.Embed(
            title=f":no_entry_sign: {title}",
            color=discord.Color.dark_red(),
            description=description or "",
        )

        await self.send(embed=em)

    async def success(self, title: str, description: str = None):
        em = discord.Embed(
            title=f":white_check_mark: {title}",
            color=discord.Color.dark_green(),
            description=description or "",
        )

        await self.send(embed=em)
