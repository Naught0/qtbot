import base64
import io
import aiohttp
import discord

from discord.ext import commands
from utils import custom_context
from time import time
from urllib.parse import quote_plus

class Dalle(commands.Cog):
    @commands.command(aliases=["ai"])
    async def dalle(self, ctx: custom_context.CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            resp: aiohttp.ClientResponse = await ctx.bot.aio_session.post("https://backend.craiyon.com/generate", json={"prompt": prompt})

            if resp.status >= 400:
                return await ctx.error("Too much traffic - try again later", f"```{resp.status}\n{resp.text}```")
            
            data = await resp.json()

            files = []
            for pic in data["images"]:
                files.append(discord.File(io.BytesIO(base64.urlsafe_b64decode(pic)), filename=f"{quote_plus(prompt)}_{time()}.png"))
            
            await ctx.send(prompt, file=files[0])
        


def setup(bot):
    bot.add_cog(Dalle(bot))