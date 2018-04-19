#!/bin/env python3

import random
import re
from datetime import datetime

import discord
from discord.ext import commands


class Generic:
    GOT_AIR_DATE = datetime.fromtimestamp(1554685200)
    GOT_LOGO = 'https://upload.wikimedia.org/wikipedia/en/d/d8/Game_of_Thrones_title_card.jpg'

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def todo(self, ctx):
        """ A to-do list for myself """
        await ctx.send('[ ] Gambling bot [ ] League Match History')

    # @commands.command()
    # async def kick(self, ctx, *args):
    #     """ Don't use this """
    #     phrases = ['I would never!', 'That isn\'t very nice!',
    #                'Maybe we should talk about our feelings.',
    #                'Calm down.', 'Check your privileges.',
    #                'Make love, not war.']
    #     await ctx.send(random.choice(phrases))

    @commands.command()
    async def say(self, ctx, *, message):
        """ Make qtbot say anything ;) """
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command()
    async def ball(self, ctx, *args):
        """ Ask the magic 8ball """
        responses = ['It is certain', 'It is decidedly so', 'Without a doubt',
                     'Yes definitely', 'You may rely on it', 'As I see it, yes',
                     'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again', 'Ask again later', 'Better not tell you now',
                     'Cannot predict now', 'Concentrate and ask again', 'Don\'t count on it',
                     'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']
        await ctx.send(random.choice(responses))

    @commands.command()
    async def same(self, ctx):
        await ctx.send('```[✓] same\n[ ] unsame```')

    @commands.command()
    async def unsame(self, ctx):
        await ctx.send('```[ ] same\n[✓] unsame```')

    @commands.command()
    async def resame(self, ctx):
        await ctx.send('```[✓] same\n[✓] re:same\n[ ] unsame```')

    @commands.command()
    async def slap(self, ctx, *, target=None):
        """ Teach someone a lesson """
        if not target:
            return await ctx.send(f'{ctx.author.name} thrusts his hands wildly about in the air.')

        await ctx.send(f'{ctx.author.name} slaps {target} around a bit with a large trout.')

    @commands.command()
    async def report(self, ctx):
        """ Report a user """
        await ctx.send(
            f'Thank you for your service. This incident has been reported to the proper authorities.'
            "We'll take it from here.")

    @commands.command()
    async def love(self, ctx, *, target=None):
        """ Give someone some lovin' """
        if ctx.author.nick is None:
            member = ctx.author
        else:
            member = ctx.author.nick

        if not target:
            return await ctx.send(f'{member} loves ... nothing')

        await ctx.send(f"{member} gives {target} some good ol' fashioned lovin'.")

    @commands.command(aliases=['at'])
    async def aesthetify(self, ctx, *, a_text):
        """ Make your message ａｅｓｔｈｅｔｉｃ，　ｍａｎ """
        ascii_to_wide = dict((i, chr(i + 0xfee0)) for i in range(0x21, 0x7f))
        ascii_to_wide.update({0x20: u'\u3000', 0x2D: u'\u2212'})

        await ctx.message.delete()
        await ctx.send(f'{a_text.translate(ascii_to_wide)}')

    @commands.command(aliases=['up'])
    async def uptime(self, ctx):
        """Get current bot uptime."""
        current_time = datetime.now()
        current_time_str = current_time.strftime('%B %d %H:%M:%S')
        await ctx.send(f'Initialized `{self.bot.start_time_str}`\n'
                       f'Current Time: `{current_time_str}`\n'
                       f'Uptime: `{str(current_time - self.bot.start_time).split(".")[0]}`')

    @commands.command(aliases=['gameofthrones', 'gotwhen'])
    async def got(self, ctx):
        """How long til the next Game of Thrones episode?"""

        delta = str(self.GOT_AIR_DATE - datetime.now())

        # Days hours minutes seconds miliseconds
        delta_list = re.sub('[^0-9 ]', ' ', delta).split()

        em = discord.Embed(title='How long til Game of Thrones?', color=discord.Color.orange())
        em.description = '`{}` days, `{}` hours, `{}` minutes, `{}` seconds'.format(*delta_list)
        em.set_thumbnail(url=self.GOT_LOGO)
        em.set_footer(text='First episode airs')
        em.timestamp = self.GOT_AIR_DATE

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Generic(bot))
