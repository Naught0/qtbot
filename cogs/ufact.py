import re
import asyncpg
import discord

from collections import namedtuple

from discord.ext import commands

from utils.custom_context import CustomContext


class UserFacts(commands.Cog):
    """
    A cog for users to add their own facts to be returned at random when called (similar to tags)
    TODO:
        Add search functionality
    """

    def __init__(self, bot):
        self.bot = bot
        self.pg_con = bot.pg_con

    @staticmethod
    def numify(s: str) -> int:
        """Small helper method to turn alphanum -> num"""
        return int(re.sub("[^0-9]", "", s))

    async def get_fact(self, guild_id: int, did: int):
        """Gets a specific fact (row from psql)"""
        query = """SELECT * from user_facts
                   WHERE guild_id = $1
                   AND id = $2;"""

        return await self.pg_con.fetchrow(query, guild_id, did)

    async def get_random_fact(self, guild_id: int):
        """Returns a random fact"""
        query = """SELECT * from user_facts
                   WHERE guild_id = $1
                   ORDER BY RANDOM()
                   LIMIT 1;"""

        return await self.pg_con.fetchrow(query, guild_id)

    async def can_delete_fact(self, ctx, did: int):
        """Check whether the user can delete a given fact

        This is essentially a tribool
            True -> Can delete
            False -> Can't delete due to permissions / ownership
            None -> Fact doesn't exist (in that guild)"""
        fact = await self.get_fact(ctx.guild.id, did)

        if not fact:
            return None

        fact_owner = fact["member_id"]

        return (
            ctx.message.channel.permissions_for(ctx.author).administrator
            or fact_owner == ctx.author.id
        )

    async def total_facts(self, ctx):
        """Check whether a server has any facts"""
        query = """SELECT COUNT(*) FROM user_facts
                   WHERE guild_id = $1;"""

        return await self.pg_con.fetchval(query, ctx.guild.id)

    @commands.group(invoke_without_command=True)
    async def ufact(self, ctx: CustomContext, fact_id: int = None):
        """Get a random user-created fact from your server"""
        # Check to see whether any facts have been created
        if await self.total_facts(ctx) < 1:
            return await ctx.error(
                "Your server does not have any facts set up!",
                description=f"Use the `{(await self.bot.get_prefix(ctx.message))[-1]}ufact add` command to "
                "start getting facts you've created.",
            )

        if fact_id:
            fact = await self.get_fact(ctx.guild.id, fact_id)
        else:
            fact = await self.get_random_fact(ctx.guild.id)

        if not fact:
            return await ctx.error(f"Couldn't find fact #{fact_id}")

        try:
            user = await ctx.guild.fetch_member(fact["member_id"])
        except discord.errors.NotFound:
            user = namedtuple(
                "User",
                (
                    "display_name",
                    "avatar_url",
                ),
            )(
                "Unknown",
                "https://ia803204.us.archive.org/4/items/discordprofilepictures/discordblue.png",
            )
        contents = fact["contents"]

        em = discord.Embed(
            title=f':bookmark: Fact #{fact["id"]}',
            description=contents,
            timestamp=fact["created"],
        )
        em.set_footer(text=f"Created by {user.display_name}", icon_url=user.display_avatar.url)

        await ctx.send(embed=em)

    @ufact.command(aliases=["create", "ad"])
    async def add(self, ctx, *, contents: str = None):
        """Add a 100% true™ fact to the database"""
        if contents is None:
            return await ctx.error("Can't add an empty fact boss, sorry!")

        query = """INSERT INTO user_facts
                   (guild_id, member_id, contents, created)
                   VALUES ($1, $2, $3, now());"""

        try:
            await self.pg_con.execute(query, ctx.guild.id, ctx.author.id, contents)
        except asyncpg.UniqueViolationError:
            return await ctx.error("Sorry, that fact already exists.")

        fact_id = await self.pg_con.fetchval(
            """SELECT id FROM user_facts WHERE contents = $1""", contents
        )
        await ctx.success(f"Added that fact for ya! (#{fact_id})")

    @ufact.command(name="delete", aliases=["remove", "del", "rm"])
    async def _delete(self, ctx, *, fact_id: str):
        """Remove a fact from the database via fact number"""
        did = self.numify(fact_id)
        can_delete = await self.can_delete_fact(ctx, did)

        if can_delete is None:
            return await ctx.error("Fact not found.")
        if not can_delete:
            return await ctx.error("You can't delete that fact.")

        query = """DELETE FROM user_facts
                   WHERE id = $1;"""
        await self.pg_con.execute(query, did)

        await ctx.success(f"Deleted fact #{did}")


async def setup(bot):
    await bot.add_cog(UserFacts(bot))
