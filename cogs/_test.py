import asyncio
import discord
from discord.ext import commands


class test:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def testme(self, ctx):
        guild = ctx.guild

        # Move to specific category
        temp_category = guild.get_channel(361378212049190922)

        if temp_category:
            channel = await guild.create_voice_channel('testing for memes')

            await channel.edit(category=temp_category)


def setup(bot):
    bot.add_cog(test(bot))
