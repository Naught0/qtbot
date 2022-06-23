import base64
import io
import json
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