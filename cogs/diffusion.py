import asyncio
import io
import json
import backoff

from typing import Literal
from urllib.parse import quote
from discord import File
from discord.ext import commands
from aiohttp import ClientResponseError, ClientResponse
from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


class Diffusion(commands.Cog):
    INPUT = {
        "version": "a9758cbfbd5f3c2094457d996681af52552901775aa2d6dd0b17fd15df959bef",
        "input": {
            "width": 512,
            "height": 512,
            "num_outputs": "1",
            "guidance_scale": 7.5,
            "prompt_strength": 0.8,
            "num_inference_steps": 50,
        },
    }
    URL = "https://api.replicate.com/v1/predictions"
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, bot: QTBot):
        with open("data/apikeys.json") as f:
            self.api_key = json.load(f)["stable_diffusion"]
        self.HEADERS.update({"Authorization": f"Token {self.api_key}"})
        self.bot = bot

    @backoff.on_exception(backoff.expo, ClientResponseError, max_tries=3)
    async def req(
        self,
        verb: Literal["GET", "POST"],
        url: str = "",
        params: dict = {},
        headers: dict = {},
        data: dict = None,
    ) -> ClientResponse:
        resp = await self.bot.aio_session.request(
            verb, f"{self.URL}{url}", params=params, headers={**headers, **self.HEADERS}, json=data
        )
        resp.raise_for_status()

        return resp

    async def start_job(self, prompt: str) -> str:
        payload = {**self.INPUT, "input": {"prompt": prompt}}
        resp = await self.req("POST", data=payload)
        resp = await resp.json()
        if resp["error"]:
            raise DiffusionError(resp["error"])

        return resp["id"]

    async def check_progress(self, id: str) -> str:
        total_checks = 0
        while True:
            resp = await self.req("GET", f"/{id}")
            resp = await resp.json()
            if total_checks >= 10:
                raise DiffusionError("Couldn't get a result after 20 seconds. Aborting.")
            if resp["error"]:
                raise DiffusionError(resp["error"])
            if resp["completed_at"]:
                return resp["output"][0]

            total_checks += 1
            await asyncio.sleep(2)

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            try:
                job_id = await self.start_job(prompt)
            except DiffusionError as e:
                return await ctx.error("API Error", str(e))
            except ClientResponseError as e:
                return await ctx.error("API Error", f"Received status code `{e.status}`\n{e.message}")

            try:
                image_url = await self.check_progress(job_id)
            except DiffusionError as e:
                return await ctx.error("API Error", str(e))
            except ClientResponseError as e:
                return await ctx.error("API Error", f"Received status code `{e.status}`\n{e.message}")

            image_data = await (await self.bot.aio_session.get(image_url)).read()

        with io.BytesIO(image_data) as f:
            return await ctx.send(f"{ctx.author.mention}: {prompt}", file=File(f, f"{quote(prompt)}.png"))


def setup(bot):
    bot.add_cog(Diffusion(bot))
