#!/bin/env python3
import discord
import asyncio
from datetime import datetime
from utils import dict_manip as dm
from discord.ext import commands

class Poll:
    def __init__(self, bot):
        self.bot = bot
        self.emoji_map = ['1\U000020e3', '2\U000020e3', '3\U000020e3', '4\U000020e3', 
                          '5\U000020e3', '6\U000020e3', '7\U000020e3', '8\U000020e3', 
                          '9\U000020e3']

    @commands.command(aliases=['survey'])
    async def poll(self, ctx, poll_name: str, timeout: float, *, poll_options: str):
        """ Create a poll for the channel to vote on 

        Usage:
        .poll 'A quoted name' 60 comma, delimited, options """ 

        if timeout > (21600):
            return await ctx.send('Please choose a timeout time which is less than 6 hours.')

        option_list = poll_options.split(',')

        if len(option_list) < 2:
            return await ctx.send('You need at least 2 options to call it a poll, jeez.')
        elif len(option_list) > len(self.emoji_map):
            return await ctx.send("That's too many options ")

        if len(poll_name) > 256:
            return await ctx.send('Sorry, titles must be under 256 characters per Discord limits.')

        # Do a heckin good embed
        em = discord.Embed(title=poll_name, color=discord.Color.teal())
        em.set_author(name=f'Poll created by {ctx.author}', icon_url=ctx.author.avatar_url)
        em.set_footer(text='Poll created at')
        em.timestamp = datetime.now()

        description_list = []
        poll_results = {}
        for idx, opt in enumerate(option_list):
            description_list.append(f'{self.emoji_map[idx]} {opt}')
            poll_results[f'{self.emoji_map[idx]}'] = {'opt': opt, 'total_votes': 0}

        em.description = '\n'.join(description_list)

        poll_msg = await ctx.send(embed=em)

        for e in self.emoji_map[:len(option_list)]:
            await poll_msg.add_reaction(e)

        def check(reaction, user):
            return user not in user_set and reaction.emoji in poll_results

        user_set = set()

        while True:
            try: 
                reaction, user = await self.bot.wait_for('reaction_add', check=check, timeout=timeout)
            except asyncio.TimeoutError:
                await poll_msg.clear_reactions()
                break
            
            if reaction.emoji in poll_results:
                user_set.add(user)
                poll_results[reaction.emoji]['total_votes'] += 1

        chan_choice = dm.key_with_max_value(poll_results)
        await ctx.send('The channel has spoken!\n'
                       f'The best option is {chan_choice} {poll_results[chan_choice]}')
        

def setup(bot):
    bot.add_cog(Poll(bot))
