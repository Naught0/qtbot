import base64
import io
from time import time
from urllib.parse import urlencode
import aiohttp
import discord
from discord.ext import commands
from utils import aiohttp_wrap as aw
from utils import custom_context

class Dalle(commands.Cog):
    @commands.command(aliases=["ai"])
    async def dalle(self, ctx: custom_context.CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            resp: aiohttp.ClientResponse = await ctx.bot.aio_session.post("https://backend.craiyon.com/generate", params={"prompt": prompt})

            if resp.status >= 400:
                return await ctx.error("Too much traffic - try again later")
            
            data = await resp.json()

            files = []
            for pic in data["images"]:
                files.append(discord.File(io.BytesIO(base64.urlsafe_b64decode(pic)), filename=f"{urlencode(prompt)}_{time.time()}.png"))
            
            await ctx.send(prompt, file=files[0])
        


def setup(bot):
    bot.add_cog(Dalle(bot))