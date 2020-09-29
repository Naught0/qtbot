import discord

from discord.ext import commands


class Quote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.color = discord.Color.gold()

    @commands.group(invoke_without_command=True)
    async def quote(self, ctx, message_id: int = None):
        """ Quote a message by using its ID """

        # Check for message_id, if it wasn't passed, return
        if message_id is None:
            return await ctx.error("Provide a message id please")

        # Just for the sake of good UX, im giving each error its own except block and message
        try:
            # Credit to Spy for this, its quite clever
            obj = discord.Object(id=message_id + 1)
            async for mess in ctx.channel.history(limit=1, before=obj):
                if mess.id == message_id:
                    message = mess
                else:
                    return await ctx.error("Message doesn't exist")
        except discord.NotFound:
            return await ctx.error("Message doesn't exist")
        except discord.Forbidden:
            return await ctx.error(
                "You do not have the permissions to request this message"
            )
        except discord.HTTPException:
            return await ctx.error("Couldn't retrieve the message")

        emb = discord.Embed(colour=self.color, description=message.content)
        emb.set_author(
            name=f"{message.author.display_name}#{message.author.discriminator}",
            icon_url=message.author.avatar_url,
        )

        # DMChannel doesn't have a name attr, not doing any fancy ternary op, its already messy
        if not isinstance(ctx.channel, discord.DMChannel):
            emb.set_footer(
                text=f'#{ctx.channel.name}'
            )

        emb.timestamp = message.created_at

        await ctx.send(embed=emb)

    @quote.command(name="fake")
    async def fake(self, ctx, message_id: int = None, *, fake_text: str = None):
        """ Make a fake quote with custom text referring to a real message by ID """
        # Check for message_id, if it wasn't passed, return
        if message_id is None:
            return await ctx.error("Provide a message id please")

        # Fake quote needs fake text, if you didn't provide it why were you using this
        if fake_text is None:
            return await ctx.error("Provide text to substitute please")

        # Just for the sake of good UX, im giving each error its own except block and message
        try:
            # Credit to Spy for this, its quite clever
            obj = discord.Object(id=message_id + 1)
            async for mess in ctx.channel.history(limit=1, before=obj):
                if mess.id == message_id:
                    message = mess
                else:
                    return await ctx.error("Message doesn't exist")
        except discord.NotFound:
            return await ctx.error("Message doesn't exist")
        except discord.Forbidden:
            return await ctx.error(
                "You do not have the permissions to request this message"
            )
        except discord.HTTPException:
            return await ctx.error("Couldn't retrieve the message")

        emb = discord.Embed(colour=self.color, description=fake_text)
        emb.set_author(
            name=f"{message.author.display_name}#{message.author.discriminator}",
            icon_url=message.author.avatar_url,
        )

        # DMChannel doesn't have a name attr, not doing any fancy ternary op, its already messy
        if not isinstance(ctx.channel, discord.DMChannel):
            emb.set_footer(
                text=f'#{ctx.channel.name}'
            )

        emb.timestamp = message.created_at

        await ctx.message.delete()

        await ctx.send(embed=emb)


def setup(bot):
    bot.add_cog(Quote(bot))
