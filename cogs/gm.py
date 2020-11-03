import json
import random

from discord.ext import commands


class GM(commands.Cog):
    def __init__(self, bot):
        with open('data/hwords.json') as f:
            self.h = json.load(f)
        with open("data/good_morning.json") as f:
            gm_dictionary = json.load(f)
        self.g = gm_dictionary["g"]
        self.m = gm_dictionary["m"]
        self.a = gm_dictionary["a"]
        self.e = gm_dictionary["e"]

    @commands.command(name="h", hidden=True)
    async def _h(self, ctx: commands.Context):
        """h"""
        await ctx.send(random.choice(self.h))

    @commands.command(name="gm", hidden=True)
    async def _gm(self, ctx: commands.Context):
        """Good morning"""
        g = random.choice(self.g)
        m = random.choice(self.m)

        await ctx.send(f"{g} {m}")

    @commands.command(name="ga", hidden=True)
    async def _ga(self, ctx: commands.Context):
        """Good afternoon"""
        g = random.choice(self.g)
        a = random.choice(self.a)

        await ctx.send(f"{g} {a}")

    @commands.command(name="ge", hidden=True)
    async def _ge(self, ctx: commands.Context):
        """Good evening"""
        g = random.choice(self.g)
        e = random.choice(self.e)

        await ctx.send(f"{g} {e}")


def setup(bot):
    bot.add_cog(GM(bot))
