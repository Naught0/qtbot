#!/bin/env python3

import discord
from discord.ext import commands

class Moderator:
    def __init__(self, bot):
        self.bot = bot

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
        """ Unban a user from the server
        Since you can't highlight them anymore use their name#discrim """
        await ctx.guild.unban(user, reason=reason)
        await ctx.send(f'User `{user}` unbanned.\n'
                       f'Reason: `{reason}`.')


def setup(bot):
    bot.add_cog(Moderator(bot))
