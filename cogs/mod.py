#!/bin/env python3

import discord
from discord.ext import commands

class Moderator:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if isinstance(error, discord.Forbidden):
            return await ctx.send('Sorry, I do not have sufficient privileges to do that.')

        if isinstance(error, discord.HTTPException):
            return await ctx.send('Sorry, something went wrong with the connection. Try again or do this manually.')

    @commands.command(aliases=['k'])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, user: discord.User, *, reason=None):
        """ Kick a user from the server """
        await ctx.guild.kick(user, reason=reason)
        await ctx.send(f'User `{user}` kicked.\n'
                       f'Reason: `{reason}`.')

    @commands.command(aliases=['kb'])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, user: discord.User, *, reason=None):
        """ Ban a user from the server """
        await ctx.guild.ban(user, reason=reason, delete_message_days=0)
        await ctx.send(f'User `{user}` banned.\n'
                       f'Reason: `{reason}`.')

    @commands.command(aliases=['ub'])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user: discord.User, *, reason=None):
        """ Unban a user from the server """
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f'User `{user}` unbanned.\n'
                       f'Reason: `{reason}`.')

def setup(bot):
    bot.add_cog(Moderator(bot))
