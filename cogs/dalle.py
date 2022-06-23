import base64
import io
from time import time
from urllib.parse import urlencode
import discord
from discord.ext import commands
from utils import aiohttp_wrap as aw
from utils import custom_context

class Dalle(commands.Cog):
    @commands.command(aliases=["ai"])
    async def dalle(self, ctx: custom_context.CustomContext, *, prompt: str) -> None:
        async with ctx.typing():
            count = 0
            while True:
                resp = await aw.aio_get_json(ctx.bot.aio_session, "https://backend.craiyon.com/generate", params={"prompt": prompt})
                count += 1
                if resp is not None:
                    break

                if count >= 5:
                    return await ctx.error("Too much traffic - try again later")

            files = []
            for pic in resp["images"]:
                files.append(discord.File(io.BytesIO(base64.urlsafe_b64decode(pic)), filename=f"{urlencode(prompt)}_{time.time()}.png"))
            
            await ctx.send(prompt, file=files[0])
        


def setup(bot):
    bot.add_cog(Dalle(bot))