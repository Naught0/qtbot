#!/bin/env python3

import discord
from discord.ext import commands

class Moderator:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.BadArgument):
            return await ctx.send(f'Sorry, I can not kick/ban that user.')

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

    @commands.command(aliases=['purge'])
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, num_msg: int):
        """ Remove bot messages from the last X messages """

        if num_msg > 100:
            return await ctx.send('Sorry, number of messages to be deleted must not exceed 100.')

        # Check so that only bot msgs are removed
        def check(message):
            return message.author.id == self.bot.user.id

        try:
            await ctx.channel.purge(check=check, limit=num_msg)
        except Exception as e:
            await ctx.send(f'Failed to delete messages.\n ```py\n{e}```')


def setup(bot):
    bot.add_cog(Moderator(bot))
