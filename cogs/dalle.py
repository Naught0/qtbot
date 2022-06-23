import base64
import io
import aiohttp
import discord

from time import time
from urllib.parse import quote_plus
from typing import List

from PIL import Image, ImageOps
from discord.ext import commands
from utils import custom_context

class Dalle(commands.Cog):
    @commands.command(aliases=["ai"])
    @commands.is_owner()
    async def dalle(self, ctx: custom_context.CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            resp: aiohttp.ClientResponse = await ctx.bot.aio_session.post("https://backend.craiyon.com/generate", json={"prompt": prompt})

            if resp.status >= 400:
                return await ctx.error("Too much traffic - try again later", f"```{resp.status}\n{await resp.text()}```")
            
            data = await resp.json()

            files = [io.BytesIO(base64.urlsafe_b64decode(pic)) for pic in data["images"]]
            stitched = self.stitch_images(files)

            image = discord.File(stitched, filename=f"{quote_plus(prompt)}_{time()}.png")

        await ctx.send(f"{prompt} {ctx.author.mention}", file=image)

    @staticmethod
    def stitch_images(images_as_bytes: List[bytes]) -> bytes:
        width, height = 256, 256
        images = [Image.open(i) for i in images_as_bytes]
        images = [ImageOps.fit(i, (256,256), Image.ANTIALIAS) for i in images]
        shape = (3,3)

        ret = Image.new("RGB", (width * shape[0], height * shape[1]))
        for row in range(shape[0]):
            for col in range(shape[1]):
                offset = width * col, height * row
                idx = row * shape[1] + col
                ret.paste(images[idx], offset)

        ret.seek(0) 
        return ret.tobytes()

def setup(bot):
    bot.add_cog(Dalle(bot))