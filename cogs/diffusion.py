import base64
import io
import os
from datetime import datetime
from urllib.parse import quote_plus

import discord
from aiohttp import ClientSession
from discord.ext import commands

from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


async def generate_image(
    session: ClientSession, endpoint: str, api_key: str, prompt: str
) -> str:
    async with session.post(
        f"https://api.runpod.ai/v2/{endpoint}/runsync",
        headers={
            "Authorization": f"Bearer {api_key}",
            "accept": "application/json",
            "content-type": "application/json",
        },
        json={
            "input": {
                "prompt": prompt[:256],
                "sampler_name": "DDIM",
                "steps": 25,
                "cfg_scale": 7,
                "width": 512,
                "height": 512,
                "batch_size": 1,
                "n_iter": 1,
            }
        },
    ) as response:
        response.raise_for_status()
        return (await response.json())["output"]["images"][0]


def image_to_discord_file(image_data: str, file_name: str) -> discord.File:
    return discord.File(
        io.BytesIO(base64.urlsafe_b64decode(image_data)), filename=file_name
    )


class Diffusion(commands.Cog):
    ENDPOINT = os.environ["RUNPOD_ENDPOINT_ID"]
    API_KEY = os.environ["RUNPOD_API_KEY"]

    def __init__(self, bot: QTBot):
        self.bot = bot

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            image = await generate_image(
                self.bot.aio_session, self.ENDPOINT, self.API_KEY, prompt
            )
            filename = f"{quote_plus(prompt)}_{int(datetime.now().timestamp())}.png"
            file = image_to_discord_file(image, filename)
            await ctx.send(f"{ctx.author.mention}: {prompt}", file=file)


async def setup(bot):
    await bot.add_cog(Diffusion(bot))
