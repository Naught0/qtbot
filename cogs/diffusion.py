import asyncio
import backoff

from typing import Any, Literal
from discord import Embed
from discord.ext import commands
from aiohttp import ClientResponseError
from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


class Diffusion(commands.Cog):
    INPUT = {
        "input": {
            "width": 512,
            "height": 512,
            "num_outputs": "1",
            "guidance_scale": 7.5,
            "prompt_strength": 0.8,
            "num_inference_steps": 50,
        }
    }
    URL = "https://replicate.com/api/models/stability-ai/stable-diffusion/versions/a9758cbfbd5f3c2094457d996681af52552901775aa2d6dd0b17fd15df959bef/predictions"

    def __init__(self, bot: QTBot):
        self.bot = bot

    @backoff.on_exception(backoff.expo, ClientResponseError, max_tries=3)
    async def req(
        self, verb: Literal["GET", "POST"], url: str = "", params: dict = None, headers: dict = None, data: dict = None
    ) -> Any:
        resp = await self.bot.aio_session.request(verb, f"{self.URL}{url}", params=params, headers=headers, json=data)
        resp.raise_for_status()

        return await resp.json()

    async def start_job(self, prompt: str) -> str:
        payload = {**self.INPUT, "prompt": prompt}
        resp = await self.req("POST", data=payload)
        if resp["error"]:
            raise DiffusionError(resp["error"])

        return resp["uuid"]

    async def check_progress(self, id: str) -> str:
        total_checks = 0
        while True:
            resp = (await self.req("GET", f"/{id}"))["prediction"]
            if total_checks >= 10:
                raise asyncio.TimeoutError("Couldn't get a result after 20 seconds. Aborting.")
            if resp["error"]:
                raise DiffusionError(resp["error"])
            if resp["completed_at"]:
                return resp["output"][0]

            total_checks += 1
            asyncio.sleep(2)

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        try:
            job_id = await self.start_job(prompt)
        except DiffusionError as e:
            return await ctx.error("API Error", str(e))
        except ClientResponseError as e:
            return await ctx.error("API Error", f"Received status code {e.status}\n{e.message}")

        try:
            image_url = await self.check_progress(job_id)
        except DiffusionError as e:
            return await ctx.error("API Error", str(e))
        except ClientResponseError as e:
            return await ctx.error("API Error", f"Received status code {e.status}\n{e.message}")

        return await ctx.send(f"{ctx.author.mention}: {prompt}\n{image_url}")


def setup(bot):
    bot.add_cog(Diffusion(bot))
