import asyncio
import io
from random import randint
import backoff

from uuid import uuid4
from typing import Literal, List
from urllib.parse import quote_plus

from discord import File
from discord.ext import commands
from aiohttp import ClientResponseError, ClientResponse

from bot import QTBot
from utils.custom_context import CustomContext


class DiffusionError(Exception):
    pass


class Diffusion(commands.Cog):
    URLS = {
        "replicate": "https://inpainter.vercel.app/api/predictions",
        "happy": "https://healthydiffusion.com/process",
    }
    HEADERS = {"Content-Type": "application/json"}

    def __init__(self, bot: QTBot):
        self.bot = bot

    async def image_to_file(self, url: str, prompt: str, spoiler: bool = False) -> File:
        image = await (await self.bot.aio_session.get(url)).read()
        return File(io.BytesIO(image), filename=f"{'SPOILER_' if spoiler else ''}{quote_plus(prompt)}.png")

    @backoff.on_exception(backoff.expo, ClientResponseError, max_tries=3, giveup=lambda x: x.status == 402)
    async def req(
        self,
        verb: Literal["GET", "POST"],
        url: str = "",
        params: dict = {},
        headers: dict = {},
        data: dict = None,
        service: Literal["replicate", "happy"] = "replicate",
    ) -> ClientResponse:
        resp = await self.bot.aio_session.request(
            verb, f"{self.URLS[service]}{url}", params=params, headers={**headers, **self.HEADERS}, json=data
        )

        resp.raise_for_status()

        return resp

    async def start_replicate_job(self, prompt: str) -> str:
        payload = {"prompt": prompt}
        resp = await self.req("POST", data=payload)
        resp = await resp.json(content_type=None)
        if resp.get("error"):
            raise DiffusionError(resp["error"])

        return resp["id"]

    async def get_replicate_output(self, id: str) -> List[str]:
        checks = 0
        while True:
            if checks >= 45:
                await self.req("POST", url=f"/{id}/cancel", data={})
                raise DiffusionError("Couldn't get a result after 90 seconds. Aborting.")

            resp = await self.req("GET", url=f"/{id}")
            resp = await resp.json(content_type=None)

            if resp.get("error"):
                raise DiffusionError(resp["error"])
            if resp["completed_at"]:
                return resp["output"]

            checks += 1
            await asyncio.sleep(2)

    @commands.command(aliases=["diffuse", "sd"])
    async def diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            try:
                job_id = await self.start_replicate_job(prompt)
                images = await self.get_replicate_output(job_id)
            except DiffusionError as e:
                return await ctx.error("API Error", f"{ctx.author.mention} {e}")
            except ClientResponseError as e:
                return await ctx.error(
                    "API Error", f"{ctx.author.mention} Received status code `{e.status}`\n{e.message}"
                )

            file = await self.image_to_file(images[0], prompt)
            return await ctx.send(f"{ctx.author.mention}: {prompt}", file=file)

    async def start_happy_job(self, text: str, unique_id: int) -> None:
        await self.req("POST", service="happy", data={"text": text, "userID": unique_id})

    async def get_happy_output(self, id: int) -> str:
        checks = 0
        while True:
            if checks >= 45:
                raise DiffusionError("Couldn't get result after 90 seconds. Aborting.")
            resp = await self.req("GET", params={"userID": id}, service="happy")
            data = await resp.json(content_type=None)
            if data["done"]:
                return data["url"]

            checks += 1
            await asyncio.sleep(2)

    @commands.command(aliases=["nsd", "nsfwsd"])
    async def nsfw_diffusion(self, ctx: CustomContext, *, prompt: str) -> None:
        is_nsfw: bool = ctx.channel.is_nsfw()
        async with ctx.typing():
            try:
                user_id = randint(0, 10**16)
                await self.start_happy_job(prompt, user_id)
                url = await self.get_happy_output(user_id)
            except DiffusionError as e:
                return await ctx.error("API Error", f"{ctx.author.mention} {e}")
            except ClientResponseError as e:
                return await ctx.error(
                    "API Error", f"{ctx.author.mention} Received status code `{e.status}`\n{e.message}"
                )

        file = await self.image_to_file(url, prompt, spoiler=not is_nsfw)
        return await ctx.send(f"{ctx.author.mention}: {prompt}", file=file)


def setup(bot):
    bot.add_cog(Diffusion(bot))
