from datetime import datetime

from discord.ext import commands
from utils.custom_context import CustomContext


class Thursday(commands.Cog):
    @commands.command(aliases=["thurs"])
    async def thursday(self, ctx: CustomContext):
        day = datetime.now().weekday()
        msg = "<a:alart:1141045442340200610> {} <a:alart:1141045442340200610>"
        if day == 3:
            msg = msg.format("***IT IS CURRENTLY THURSDAY***")
        else:
            msg = msg.format("***THE CURRENT DAY IS NOT THURSDAY***")

        return await ctx.send(msg)


def setup(bot):
    bot.add_cog(Thursday(bot))
