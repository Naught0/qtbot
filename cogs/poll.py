#!/bin/env python3

import discord
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
        elif len(option_list) > len(emoji_map):
            return await ctx.send("That's too many options ")

        if len(poll_name) > 256:
            return await ctx.send('Sorry, titles must be under 256 characters per Discord limits.')

        # Do a heckin good embed
        em = discord.Embed(title=poll_name, color=discord.Color.teal())
        em.set_footer(text=f'Poll created by {ctx.author}', icon_url=ctx.author.avatar_url)



        description_list = []
        for idx, opt in enumerate(poll_options):
            description_list.append(f'{self.emoji_map[idx]} {opt}')

        em.description = '\n'.join(description_list)

        poll_msg = await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Poll(bot))
