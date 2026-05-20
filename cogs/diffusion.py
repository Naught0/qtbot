import os
from typing import TypedDict

import discord
from aiohttp import ClientSession, ClientTimeout
from discord.ext import commands

from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


class Output(TypedDict):
    cost: float
    result: str


async def generate_image(
    session: ClientSession, endpoint: str, api_key: str, prompt: str, negative_prompt=""
) -> Output:
    async with session.post(
        f"https://api.runpod.ai/v2/{endpoint}/runsync",
        timeout=ClientTimeout(120),
        headers={
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json",
            "content-type": "application/json",
        },
        json={
            "input": {
                "prompt": prompt[:256],
                "enable_safety_checker": bool(negative_prompt),
                "size": "512*512",
            }
        },
    ) as response:
        response.raise_for_status()
        return (await response.json())["output"]


def make_embed(prompt: str, output: Output) -> discord.Embed:
    em = discord.Embed(description=f"{prompt}", color=discord.Color.blurple())
    em.set_image(url=output["result"])
    em.set_footer(text=f"Cost: ${output['cost']:.4f}")

    return em


class Diffusion(commands.Cog):
    ENDPOINT = os.environ["RUNPOD_ENDPOINT_ID"]
    API_KEY = os.environ["RUNPOD_API_KEY"]
    ENABLED_GUILDS = set(int(id) for id in os.environ["AI_ENABLED_GUILDS"].split(","))
    SFW_NEGATIVE_PROMPT = os.environ["SFW_NEGATIVE_PROMPT"]

    def __init__(self, bot: QTBot):
        self.bot = bot

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        if not ctx.guild or ctx.guild.id not in self.ENABLED_GUILDS:
            return

        async with ctx.typing():
            output = await generate_image(
                self.bot.aio_session,
                self.ENDPOINT,
                self.API_KEY,
                prompt,
                self.SFW_NEGATIVE_PROMPT,
            )
            await ctx.send(ctx.author.mention, embed=make_embed(prompt, output))

    @commands.command(name="nsd", hidden=True)
    async def unrestricted_diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        if not ctx.guild or ctx.guild.id not in self.ENABLED_GUILDS:
            return

        async with ctx.typing():
            output = await generate_image(
                self.bot.aio_session, self.ENDPOINT, self.API_KEY, prompt
            )
            await ctx.send(ctx.author.mention, embed=make_embed(prompt, output))


async def setup(bot):
    await bot.add_cog(Diffusion(bot))
