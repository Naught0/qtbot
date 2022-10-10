import base64
import io
import aiohttp
import backoff
import discord

from time import time
from urllib.parse import quote_plus

from discord.ext import commands
from utils import custom_context
from utils.images import stitch_images


class Dalle(commands.Cog):
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
    async def _get_dalle(self, ctx: custom_context.CustomContext, prompt: str):
        resp: aiohttp.ClientResponse = await ctx.bot.aio_session.post(
            "https://backend.craiyon.com/generate", json={"prompt": prompt}
        )
        resp.raise_for_status()

        return await resp.json()

    @commands.command(aliases=["ai"])
    async def dalle(self, ctx: custom_context.CustomContext, *, prompt: str) -> None:
        """Create 9 AI generated images from a prompt sentence or description

        Args:
            ctx (custom_context.CustomContext)
            prompt (str)
        """
        async with ctx.typing():
            try:
                data = await self._get_dalle(ctx, prompt)
            except aiohttp.ClientError:
                return await ctx.error("DALLe machine broke - too much traffic")

            files = [io.BytesIO(base64.urlsafe_b64decode(pic)) for pic in data["images"]]
            stitched = stitch_images(files, rows_cols=3)
            image = discord.File(stitched, filename=f"{quote_plus(prompt)}_{time()}.png")

        await ctx.send(f"{ctx.author.mention}: {prompt}", file=image)


def setup(bot):
    bot.add_cog(Dalle(bot))
