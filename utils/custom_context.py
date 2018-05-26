import discord
from discord.ext import commands


class CustomContext(commands.Context):
    async def error(self, message: str):
        em = discord.Embed(title=f':no_entry_sign: {message}',
                           color=discord.Color.dark_red())

        await self.send(embed=em)

    async def success(self, message: str):
        em = discord.Embed(title=f':white_check_mark: {message}',
                           color=discord.Color.dark_green())

        await self.send(embed=em)
