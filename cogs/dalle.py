import asyncio
import base64
import io
import aiohttp
import backoff
import discord

from time import time
from urllib.parse import quote_plus
from typing import List

from PIL import Image
from discord.ext import commands
from utils import custom_context

class Dalle(commands.Cog):
    @backoff.on_exception(backoff.expo, aiohttp.ClientError, max_tries=3)
    async def _get_dalle(self, ctx: custom_context.CustomContext, prompt: str):
        resp: aiohttp.ClientResponse = await ctx.bot.aio_session.post("https://backend.craiyon.com/generate", json={"prompt": prompt})
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
            data = await self._get_dalle(ctx, prompt)

            files = [io.BytesIO(base64.urlsafe_b64decode(pic)) for pic in data["images"]]
            stitched = self.stitch_images(files)
            image = discord.File(stitched, filename=f"{quote_plus(prompt)}_{time()}.png")

        await ctx.send(f"{ctx.author.mention}: {prompt}", file=image)

    @staticmethod
    def stitch_images(images_as_bytes: List[bytes]) -> io.BytesIO:
        """https://stackoverflow.com/questions/33101935/convert-pil-image-to-byte-array

        Args:
            images_as_bytes (List[bytes])

        Returns:
            io.BytesIO
        """
        images = [Image.open(i) for i in images_as_bytes]
        rows, cols = 3, 3
        w, h = images[0].size
        grid = Image.new("RGB", size=(cols*w, rows*h))

        for idx, img in enumerate(images):
            grid.paste(img, box=(idx%cols*w, idx//cols*h))

        ret = io.BytesIO() 
        grid.save(ret, "PNG")

        ret.seek(0)
        return ret

def setup(bot):
    bot.add_cog(Dalle(bot))
