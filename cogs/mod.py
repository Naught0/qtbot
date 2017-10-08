#!/bin/env python3

import discord
from discord.ext import commands

class Moderator:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['k'])
    async def kick(self, ctx, user: discord.User, *, reason=None):
        """ Kick a user from the server """
        try:
            await ctx.guild.kick(user, reason=reason)
        except discord.Forbidden:
            await ctx.send('Insufficient privilges.')
        except discord.HTTPException:
            await ctx.send('Welp, Discord is having a bad time right now. Try doing this manually instead.')
        else:
            await ctx.send(f'User `{user}` kicked.\n'
                           f'Reason: `{reason}`.')

    @commands.command(aliases=['kb'])
    async def ban(self, ctx, user: discord.User, *, reason=None):
        """ Ban a user from the server """
        try:
            await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        except discord.Forbidden:
            await ctx.send('Insufficient privilges.')
        except discord.HTTPException:
            await ctx.send('Welp, Discord is having a bad time right now. Try doing this manually instead.')
        else:
            await ctx.send(f'User `{user}` banned.\n'
                           f'Reason: `{reason}`.')

    @commands.command(aliases=['ub'])
    async def unban(self, ctx, user: discord.User, *, reason=None):
        """ Unban a user from the server """
        try:
            await ctx.guild.unban(user, reason=reason, delete_message_days=0)
        except discord.Forbidden:
            await ctx.send('Insufficient privilges.')
        except discord.HTTPException:
            await ctx.send('Welp, Discord is having a bad time right now. Try doing this manually instead.')
        else:
            await ctx.send(f'User `{user}` unbanned.\n'
                           f'Reason: `{reason}`.')

def setup(bot):
    bot.add_cog(Moderator(bot))
