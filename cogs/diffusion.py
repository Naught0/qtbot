import asyncio
import io
import json
import backoff

from typing import Literal, List
from itertools import cycle
from urllib.parse import quote

from discord import File
from discord.ext import commands
from aiohttp import ClientResponseError, ClientResponse

from bot import QTBot
from utils.custom_context import CustomContext
from utils.images import stitch_images


class DiffusionError(Exception):
    pass


class Diffusion(commands.Cog):
    INPUT = {
        "version": "a9758cbfbd5f3c2094457d996681af52552901775aa2d6dd0b17fd15df959bef",
        "input": {
            "width": 256,
            "height": 256,
            "num_outputs": 1,
        },
    }
    URL = "https://api.replicate.com/v1/predictions"
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, bot: QTBot):
        with open("data/apikeys.json") as f:
            self.api_keys = cycle(json.load(f)["stable_diffusion"])

        self.HEADERS["Authorization"] = f"Token {next(self.api_keys)}"
        self.bot = bot

    @backoff.on_exception(backoff.expo, ClientResponseError, max_tries=3, giveup=lambda x: x.status == 402)
    async def req(
        self,
        verb: Literal["GET", "POST"],
        url: str = "",
        params: dict = {},
        headers: dict = {},
        data: dict = None,
    ) -> ClientResponse:
        attempt_count = 0
        while True:
            if attempt_count > 4:
                break
            attempt_count += 1
            resp = await self.bot.aio_session.request(
                verb, f"{self.URL}{url}", params=params, headers={**headers, **self.HEADERS}, json=data
            )
            if resp.status == 402:
                self.HEADERS["Authorization"] = f"Token {next(self.api_keys)}"
                continue

            break

        resp.raise_for_status()

        return resp

    async def start_job(self, prompt: str) -> str:
        payload = {**self.INPUT, "input": {**self.INPUT["input"], "prompt": prompt}}
        resp = await self.req("POST", data=payload)
        resp = await resp.json()
        if resp["error"]:
            raise DiffusionError(resp["error"])

        return resp["id"]

    async def check_progress(self, id: str) -> List[str]:
        total_checks = 0
        while True:
            resp = await self.req("GET", f"/{id}")
            resp = await resp.json()
            if total_checks >= 15:
                raise DiffusionError("Couldn't get a result after 30 seconds. Aborting.")
            if resp["error"]:
                raise DiffusionError(resp["error"])
            if resp["completed_at"]:
                return resp["output"]

            total_checks += 1
            await asyncio.sleep(2)

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            try:
                job_id = await self.start_job(prompt)
            except DiffusionError as e:
                return await ctx.error("API Error", f"{ctx.author.mention} {e}")
            except ClientResponseError as e:
                return await ctx.error(
                    "API Error", f"{ctx.author.mention} Received status code `{e.status}`\n{e.message}"
                )

            try:
                images = await self.check_progress(job_id)
            except DiffusionError as e:
                return await ctx.error("API Error", str(e))
            except ClientResponseError as e:
                return await ctx.error(
                    "API Error", f"{ctx.author.mention} Received status code `{e.status}`\n{e.message}"
                )

            image = await (await self.bot.aio_session.get(images[0])).read()
            file = File(image, filename=f"{quote(prompt)}.png")

        return await ctx.send(f"{ctx.author.mention}: {prompt}", file=file)


def setup(bot):
    bot.add_cog(Diffusion(bot))
