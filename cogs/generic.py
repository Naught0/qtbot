import discord
from discord.ext import commands
import random


class Generic():
    def __init__(self, bot):
        self.bot = bot

    @commands.bot.command()
    async def todo(self):
        return await self.bot.say("[ ] Gambling bot [ ] League Match History [ ] Google")

    # No kicking allowed
    @commands.bot.command()
    async def kick(self, *args):
        """Don't use this"""
        phrases = ["I would never!", "That isn't very nice!",
                   "Maybe we should talk about our feelings.", 
                   "Calm down.", "Check your privileges.",
                   "Make love, not war."]
        return await self.bot.say(phrases[random.randint(0, len(phrases) - 1)])

    @commands.bot.command(pass_context=True)
    async def say(self, ctx, *args):
        await self.bot.delete_message(ctx.message)
        return await self.bot.say(" ".join(args))

    # Returns pseudo-random magic 8-ball result
    @commands.bot.command()
    async def ball(self, *args):
        """ Ask the magic 8ball """
        responses = ["It is certain", "It is decidedly so", "Without a doubt",
                     "Yes definitely", "You may rely on it", "As I see it, yes",
                     "Most likely", "Outlook good", "Yes", "Signs point to yes",
                     "Reply hazy try again", "Ask again later", "Better not tell you now",
                     "Cannot predict now", "Concentrate and ask again", "Don't count on it",
                     "My reply is no", "My sources say no", "Outlook not so good", "Very doubtful"]
        return await self.bot.say(responses[random.randint(0, len(responses) - 1)])

    # Same!
    @commands.bot.command()
    async def same(self):
        return await self.bot.say("\n[✓] same\n[ ] unsame")

    # Unsame!
    @commands.bot.command()
    async def unsame(self):
        return await self.bot.say("\n[ ] same\n[✓] unsame")

    # Resame!
    @commands.bot.command()
    async def resame(self):
        return await self.bot.say("\n[✓] same\n [✓] re:same\n [ ] unsame")

    @commands.bot.command(pass_context=True)
    async def slap(self, ctx, *args):
        if not args:
            return await self.bot.say("You can't slap nothing.")

        member = str(ctx.message.author).split("#")
        return await self.bot.say("{} slaps {} around a bit with a large trout.".format(member[0], args[0]))

    @commands.bot.command(pass_context=True)
    async def love(self, ctx, *args):
        member = str(ctx.message.author).split("#")

        if not args:
            return await self.bot.say("{} loves ... nothing".format(member[0]))

        return await self.bot.say("{} gives {} some good ol' fashioned lovin'". format(member[0], args[0]))


def setup(bot):
    bot.add_cog(Generic(bot))
