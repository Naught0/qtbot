import random
import re
from datetime import datetime

import discord
from discord.ext import commands


class Generic(commands.Cog):
    DICE_PATTERN = re.compile("\d+d\d+")

    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.dark_blue()

    @commands.command(name="decide")
    async def _decide(self, ctx: commands.Context, *, to_decide: str):
        """Decide between a list of comma separated options"""
        options = [x.strip() for x in to_decide.split(",")]
        choice = random.choice(options)

        await ctx.send(
            embed=discord.Embed(color=discord.Color.blurple(), description=choice)
        )

    @commands.command(name="await", hidden=True)
    async def _await(self, ctx: commands.Context):
        reactions = ["🅰️", "🇼", "🇦", "🇮", "🇹"]
        for reaction in reactions:
            await ctx.message.add_reaction(reaction)

    @commands.command(name="roll", aliases=["dice"])
    async def _roll(self, ctx: commands.Context, *, dice: str):
        """Roll some dice
        Format: XdY - where 1 <= X <= 10 and 1 <= Y <= 100
        Example: qt.roll 3d6"""
        if not self.DICE_PATTERN.match(dice.lower()):
            return await ctx.error(
                "Roll must be in the format XdY",
                description="where 1 <= X <= 10 and 1 <= Y <= 100",
            )
        else:
            match = self.DICE_PATTERN.match(dice.lower()).group()

        num, sides = [int(x) for x in match.split("d")]
        if num < 1 or num > 10 or sides < 1 or sides > 100:
            return await ctx.error(
                "Roll must be in the format XdY",
                description="where 1 <= X <= 10 and 1 <= Y <= 100",
            )

        rolls = [random.choice(range(1, sides + 1)) for x in range(num)]

        em = discord.Embed(color=discord.Color.blurple())
        em.set_author(
            name=f"{ctx.author.display_name} rolled {num}d{sides}",
            icon_url=ctx.author.avatar_url,
        )
        em.add_field(name=":game_die: Rolls", value=", ".join([str(x) for x in rolls]))
        em.add_field(name=":game_die: Total", value=str(sum(rolls)), inline=False)

        await ctx.send(embed=em)

    @commands.command(hidden=True)
    async def say(self, ctx: commands.Context, *, message):
        """ Make qtbot say anything ;) """
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name="8ball", aliases=["ball"])
    async def ball(self, ctx: commands.Context, *, query=None):
        """ Ask the magic 8ball """
        if query is None:
            return await ctx.error("The 8Ball's wisdom is not to be wasted.")

        responses = [
            "It is certain",
            "It is decidedly so",
            "Without a doubt",
            "Yes definitely",
            "You may rely on it",
            "As I see it, yes",
            "Most likely",
            "Outlook good",
            "Yes",
            "Signs point to yes",
            "Reply hazy try again",
            "Ask again later",
            "Better not tell you now",
            "Cannot predict now",
            "Concentrate and ask again",
            "Don't count on it",
            "My reply is no",
            "My sources say no",
            "Outlook not so good",
            "Very doubtful",
        ]

        if not query.endswith("?"):
            query = f"{query}?"

        await ctx.send(
            embed=discord.Embed(
                title=f":8ball: {query}",
                description=random.choice(responses),
                color=self.blue,
            )
        )

    @commands.command()
    async def same(self, ctx):
        await ctx.send(":white_check_mark: same\n:green_square: unsame")

    @commands.command()
    async def unsame(self, ctx):
        await ctx.send(":green_square: same\n:white_check_mark: unsame")

    @commands.command()
    async def resame(self, ctx):
        await ctx.send(":white_check_mark: same\n:white_check_mark: re:same\n:green_square: unsame")

    @commands.command()
    async def slap(self, ctx: commands.Context, *, target=None):
        """ Teach someone a lesson """
        if target is None:
            return await ctx.send(
                f"{ctx.author.name} thrusts his hands wildly about in the air."
            )

        await ctx.send(
            f"{ctx.author.name} slaps {target} around a bit with a large trout."
        )

    @commands.command()
    async def report(self, ctx):
        """ Report a user """
        await ctx.success(
            f"Thank you for your report. This incident has been sent to the proper authorities. "
            "We'll take it from here."
        )

    @commands.command()
    async def love(self, ctx: commands.Context, *, target=None):
        """ Give someone some lovin' """

        if not target:
            return await ctx.send(f"{ctx.author.display_name} loves ... nothing")

        await ctx.send(
            f":heart_decoration: {ctx.author.display_name} gives {target} some good ol' fashioned lovin'. :heart_decoration:"
        )

    @commands.command(aliases=["at"])
    async def aesthetify(self, ctx: commands.Context, *, a_text):
        """ Make your message ａｅｓｔｈｅｔｉｃ，　ｍａｎ """
        ascii_to_wide = dict((i, chr(i + 0xFEE0)) for i in range(0x21, 0x7F))
        ascii_to_wide.update({0x20: "\u3000", 0x2D: "\u2212"})

        await ctx.message.delete()
        await ctx.send(f"{a_text.translate(ascii_to_wide)}")

    @commands.command(aliases=["up"])
    async def uptime(self, ctx):
        """Get current bot uptime."""
        current_time = datetime.now()
        em = discord.Embed(title=":clock1: Qtbot Uptime", color=self.blue)
        em.add_field(name="Initialized", value=self.bot.start_time_str, inline=False)
        em.add_field(
            name="Uptime", value=str(current_time - self.bot.start_time).split(".")[0]
        )

        await ctx.send(embed=em)

    @commands.command(aliases=["pong"])
    async def ping(self, ctx):
        """See the bot's latency"""
        latency = ctx.bot.latency * 1000
        em = discord.Embed(
            title=":ping_pong: Pong!",
            description=f"**Bot latency:** ```{latency:.2f} ms```",
            color=self.blue,
        )

        await ctx.send(embed=em)

    @commands.command()
    async def about(self, ctx):
        """Get information about qtbot"""
        em = discord.Embed(
            title=":information_source: About qtbot",
            description="Qtbot is a general purpose bot with a load of functionality. Call the help"
            " command via `qt.help` to receive a message with a full list of commands.",
            color=self.blue,
        )
        em.add_field(name="Total Servers", value=f"`{len(self.bot.guilds):,}`")
        em.add_field(name="Total Users", value=f"`{len(self.bot.users):,}`")
        em.add_field(name="Total Commands", value=f"`{len(self.bot.commands)}`")
        em.add_field(
            name="Disclaimer",
            value="Qtbot does not collect messages or information on any users unless "
            "that user specifically opts to share it via a command. Information "
            "that may be willingly shared includes:\n"
            "\u2022 `Location (for weather & forecast)`\n"
            "\u2022 `League of Legends username`\n"
            "\u2022 `Oldschool Runescape username`\n"
            "\u2022 `A link to an Oldschool Runescape screenshot`\n"
            "If you have any questions about this contact the owner below.",
        )
        em.add_field(name="Owner", value="`naught0#4417`")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Generic(bot))
