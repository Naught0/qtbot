import discord
from discord.ext import commands

"""
This would work if I wasn't hosting my bot with Digital Ocean.
Google blocks me because they hate me personally.
"""

class RIS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.aiohttp_session = bot.aio_session
        self.gyaku_url = 'http://localhost:8000/search'

    @commands.command(aliases=['ris'])
    async def reverse_image_search(self, ctx, *, url: str):
        """ Do a google reverse image search """
        async with self.aiohttp_session.post(self.gyaku_url, data=url) as r:
            resp_data = await r.text()

        await ctx.send(f'```{resp_data}```')
        # if resp_data['error'] is not None:
        #     return await ctx.send(f'Sorry, I could not find anything for that one.\n```{resp_data["error"]}```')
        #
        # em = discord.Embed(title=':frame_photo: Image Search Results', color=discord.Color.dark_blue())
        #
        # if resp_data['best_guess']:
        #     em.add_field(name='Best guess', value=resp_data['best_guess'])
        #
        # await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(RIS(bot))
