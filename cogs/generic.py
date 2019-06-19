import random
import re
from datetime import datetime

import discord
from discord.ext import commands


class Generic(commands.Cog):
    GOT_AIR_DATE = datetime.fromtimestamp(1555236000)
    GOT_LOGO = 'https://upload.wikimedia.org/wikipedia/en/d/d8/Game_of_Thrones_title_card.jpg'

    def __init__(self, bot):
        self.bot = bot
        self.blue = discord.Color.dark_blue()

    @commands.command(hidden=True)
    async def say(self, ctx, *, message):
        """ Make qtbot say anything ;) """
        await ctx.message.delete()
        await ctx.send(message)

    @commands.command(name='8ball', aliases=['ball'])
    async def ball(self, ctx, *, query=None):
        """ Ask the magic 8ball """
        if query is None:
            return await ctx.error("The 8Ball's wisdom is not to be wasted.")

        responses = ['It is certain', 'It is decidedly so', 'Without a doubt',
                     'Yes definitely', 'You may rely on it', 'As I see it, yes',
                     'Most likely', 'Outlook good', 'Yes', 'Signs point to yes',
                     'Reply hazy try again', 'Ask again later', 'Better not tell you now',
                     'Cannot predict now', 'Concentrate and ask again', 'Don\'t count on it',
                     'My reply is no', 'My sources say no', 'Outlook not so good', 'Very doubtful']

        if not query.endswith('?'):
            query = f'{query}?'

        await ctx.send(embed=discord.Embed(title=f':8ball: {query}',
                                           description=random.choice(responses),
                                           color=self.blue))

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
        if target is None:
            return await ctx.send(f'{ctx.author.name} thrusts his hands wildly about in the air.')

        await ctx.send(f'{ctx.author.name} slaps {target} around a bit with a large trout.')

    @commands.command()
    async def report(self, ctx):
        """ Report a user """
        await ctx.success(
            f'Thank you for your report. This incident has been sent to the proper authorities. '
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

        await ctx.send(f":heart_decoration: {member} gives {target} some good ol' fashioned lovin'. :heart_decoration:")

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
        em = discord.Embed(title=':clock1: Qtbot Uptime', color=self.blue)
        em.add_field(name='Initialized', value=self.bot.start_time_str, inline=False)
        em.add_field(name='Current time (EST)', value=current_time_str, inline=False)
        em.add_field(name='Uptime', value=str(current_time - self.bot.start_time).split('.')[0])

        await ctx.send(embed=em)

    @commands.command(aliases=['pong'])
    async def ping(self, ctx):
        """See the bot's latency"""
        latency = ctx.bot.latency * 1000
        em = discord.Embed(title=':ping_pong: Pong!',
                           description=f'**Bot latency:** ```{latency:.2f} ms```',
                           color=self.blue)

        await ctx.send(embed=em)

    @commands.command()
    async def about(self, ctx):
        """Get information about qtbot"""
        em = discord.Embed(title=':information_source: About qtbot',
                           description='Qtbot is a general purpose bot with a load of functionality. Call the help'
                                       ' command via `qt.help` to receive a message with a full list of commands.',
                           color=self.blue)
        em.add_field(name='Total Servers', value=f'`{len(self.bot.guilds):,}`')
        em.add_field(name='Total Users', value=f'`{len(self.bot.users):,}`')
        em.add_field(name='Total Commands', value=f'`{len(self.bot.commands)}`')
        em.add_field(name='Disclaimer', value='Qtbot does not collect messages or information on any users unless '
                                              'that user specifically opts to share it via a command. Information '
                                              'that may be willingly shared includes:\n'
                                              '\u2022 `Location (for weather & forecast)`\n'
                                              '\u2022 `League of Legends username`\n'
                                              '\u2022 `Oldschool Runescape username`\n'
                                              '\u2022 `A link to an Oldschool Runescape screenshot`\n'
                                              'If you have any questions about this contact the owner below.')
        em.add_field(name='Owner', value='`naught0#4417`')

        await ctx.send(embed=em)



def setup(bot):
    bot.add_cog(Generic(bot))
