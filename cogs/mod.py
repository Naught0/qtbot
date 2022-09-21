import discord
from discord.ext import commands


# This bit allows me to more easily unban members via ID or name#discrim
# Taken mostly from R. Danny
# https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py#L83-L94
class BannedMember(commands.Converter):
    async def convert(self, ctx, arg):
        bans = await ctx.guild.bans()

        try:
            member_id = int(arg)
            user = discord.utils.find(lambda u: u.user.id == member_id, bans)
        except ValueError:
            user = discord.utils.find(lambda u: str(u.user) == arg, bans)

        if user is None:
            return None

        return user


class Moderator(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pg = bot.pg_con

    @commands.command(aliases=["k"])
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason=None):
        """Kick a member from the server"""
        await ctx.guild.kick(member, reason=reason)
        await ctx.send(f"Member `{member}` kicked.\n" f"Reason: `{reason}`.")

    @commands.command(aliases=["kb"])
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason=None):
        """Ban a member from the server"""
        await ctx.guild.ban(member, reason=reason, delete_message_days=0)
        await ctx.send(f"Member `{member}` banned.\n" f"Reason: `{reason}`.")

    @commands.command(aliases=["ub"])
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, member: BannedMember, *, reason=None):
        """Unban a member from the server
        Since you can't highlight them anymore use their name#discrim or ID"""
        if member is not None:
            await ctx.guild.unban(member.user, reason=reason)
            await ctx.send(f"Member `{member.user}` unbanned.\n" f"Reason: `{reason}`.")

        else:
            await ctx.send("Sorry, I couldn't find that user. Maybe they're not banned :thinking:")

    @commands.command(aliases=["purge"])
    @commands.has_permissions(manage_messages=True)
    async def clean(self, ctx, num_msg: int):
        """Remove bot messages from the last X messages"""
        if num_msg > 100:
            return await ctx.send("Sorry, number of messages to be deleted must not exceed 100.")

        # Check so that only bot msgs are removed
        def check(message):
            return message.author.id == self.bot.user.id

        try:
            await ctx.channel.purge(check=check, limit=num_msg)
        except Exception as e:
            await ctx.send(f"Failed to delete messages.\n ```py\n{e}```")

    @commands.command(name="prefix", aliases=["set_pre", "pre"])
    @commands.has_permissions(manage_guild=True)
    async def set_prefix(self, ctx, *, prefix: str = None):
        """Set the server's command prefix for qtbot"""
        # Return prefix if not provided with a change
        if not prefix:
            prefixes = await ctx.bot.get_prefix(ctx.message)

            # If there is only 1 prefix, this returns a string
            # Transform to a tuple so the loop logic works later on
            if type(prefixes) != tuple:
                prefixes = tuple([prefixes])

            em = discord.Embed(color=discord.Color.blurple())
            em.set_author(
                name=f"{'Bot prefix' if len(prefixes) == 1 else 'Bot Prefixes'} for {ctx.guild.name}",
                icon_url=ctx.guild.icon_url,
            )
            em.set_footer(text="Use qt.pre <New_Prefix> to set a new prefix")

            em.description = "\n".join([f"\u2022 `{x}`" for x in prefixes])
            return await ctx.send(embed=em)

        execute = f"""INSERT INTO custom_prefix (guild_id, prefix) VALUES ({ctx.guild.id}, $1)
                      ON CONFLICT (guild_id) DO 
                          UPDATE SET prefix = $1;"""
        try:
            await self.pg.execute(execute, prefix)
        except Exception as e:
            print(e)
            await ctx.send(f"Sorry, couldn't change prefix to `{prefix}`.")
        else:
            # Update the prefix dict
            self.bot.pre_dict[ctx.guild.id] = prefix

        await ctx.send(f"Changed command prefix to `{prefix}`.")


def setup(bot):
    bot.add_cog(Moderator(bot))
