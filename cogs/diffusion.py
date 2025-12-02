import base64
import io
import os
from datetime import datetime
from urllib.parse import quote_plus

import discord
from aiohttp import ClientSession, ClientTimeout
from discord.ext import commands

from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


async def generate_image(
    session: ClientSession, endpoint: str, api_key: str, prompt: str, negative_prompt=""
) -> str:
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
                "negative_prompt": negative_prompt,
                "num_inference_steps": 7,
            }
        },
    ) as response:
        response.raise_for_status()
        return (await response.json())["output"]["images"][0]["image"]


def image_to_discord_file(image_data: str, file_name: str) -> discord.File:
    return discord.File(
        io.BytesIO(base64.urlsafe_b64decode(image_data)), filename=file_name
    )


def make_file_name(prompt: str) -> str:
    return f"{quote_plus(prompt)}_{int(datetime.now().timestamp())}.png"


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
            image = await generate_image(
                self.bot.aio_session,
                self.ENDPOINT,
                self.API_KEY,
                prompt,
                self.SFW_NEGATIVE_PROMPT,
            )
            file = image_to_discord_file(image, make_file_name(prompt))
            await ctx.send(f"{ctx.author.mention}: {prompt}", file=file)

    @commands.command(name="nsd", hidden=True)
    async def unrestricted_diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        if not ctx.guild or ctx.guild.id not in self.ENABLED_GUILDS:
            return

        async with ctx.typing():
            image = await generate_image(
                self.bot.aio_session, self.ENDPOINT, self.API_KEY, prompt
            )
            file = image_to_discord_file(image, f"SPOILER_{make_file_name(prompt)}")
            await ctx.send(
                f"{ctx.author.mention}: {prompt}",
                file=file,
            )


async def setup(bot):
    await bot.add_cog(Diffusion(bot))
