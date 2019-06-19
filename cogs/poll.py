import discord
import asyncio
from datetime import datetime
from functools import reduce
from utils import dict_manip as dm
from discord.ext import commands

class Poll(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.emoji_tup = tuple([f'{x}\U000020e3' for x in range(1, 10)])

    @commands.command(aliases=['survey'])
    async def poll(self, ctx, poll_name: str, timeout: float, *, poll_options: str):
        """ Create a poll for the channel to vote on 

        Usage:
        .poll 'A quoted name' 60 comma, delimited, options """ 

        if timeout > (21600):
            return await ctx.send('Please choose a timeout time which is less than 6 hours.')

        option_list = poll_options.split(',')

        # Gotta have options
        if len(option_list) < 2:
            return await ctx.send('You need at least 2 options to call it a poll, jeez.')

        # 9 is options thanks
        elif len(option_list) > len(self.emoji_tup):
            return await ctx.send("That's too many options ")

        # Poll name will cause an error if above this value
        if len(poll_name) > 256:
            return await ctx.send('Sorry, titles must be under 256 characters per Discord limits.')

        # Do a heckin good embed
        em = discord.Embed(title=poll_name, color=discord.Color.teal())
        em.set_author(name=f'Poll created by {ctx.author}', icon_url=ctx.author.avatar_url)
        em.set_footer(text='Poll created at')
        em.timestamp = datetime.now()

        poll_results = {}
        for idx, opt in enumerate(option_list):
            # Set votes to -1 so as not to count bot reactions
            poll_results[self.emoji_tup[idx]] = {'opt_text': f'{self.emoji_tup[idx]} {opt}', 'votes': -1}

        em.description = '\n'.join([x['opt_text'] for x in poll_results.values()])

        # Save message obj to a variable
        poll_msg = await ctx.send(embed=em)

        # Add as many reactions as options
        for e in poll_results:
            await poll_msg.add_reaction(e)

        # Checks whether user has already voted & whether their emoji is allowed
        def check(reaction, user):
            return user not in user_set and reaction.emoji in poll_results

        # User set because hashes are freaky-fast
        # Thanks Beat (:
        user_set = set()

        while True:
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=timeout)
            except asyncio.TimeoutError:
                await poll_msg.clear_reactions()
                break

            user_set.add(user)
            poll_results[reaction.emoji]['votes'] += 1

        # Thanks to Jared for this lamda / reduce
        predicate = lambda x, y: x if poll_results[x]['votes'] > poll_results[y]['votes'] else y
        chan_choice = reduce(predicate, poll_results.keys())
        await ctx.send('The channel has spoken!\n'
                       f'The best option is "{poll_results[chan_choice]["opt_text"]}", with `{poll_results[chan_choice]["votes"]}` vote(s).')
        

def setup(bot):
    bot.add_cog(Poll(bot))
