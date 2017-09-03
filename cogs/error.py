#!/bin/env python

import discord.ext


class ErrorHandler:
    def __init__(self, bot):
        self.bot = bot

    async def on_command_error(self, ctx, error):
        """ Handle command errors more gracefully """

        if isistance(error, discord.ext.commands.CommandNotFound):
            return

        if isinstance(error, discord.ext.commands.errors.NotOwner):
            return await ctx.send('Sorry, only the owner of qtbot may run this command.')

        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            return await ctx.send(f'This command is on cooldown. Please retry in {error.retry_after} second(s).')

        if isinstance(error, discord.ext.commands.BotMissingPermissions):
            return await ctx.send(f'I can\'t do that! I\'m missing permissions: ```{"\n".join(error.missing_perms)}```')

        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            return await ctx.send(f'Command missing required argument `{error.param}`')


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
