import asyncpg
import discord
from discord.ext import commands


class UserFacts:
    """
    A cog for users to add their own facts to be returned at random when called (similar to tags)
    TODO:
        Add search functionality
    """

    def __init__(self, bot):
        self.bot = bot
        self.pg_con = bot.pg_con

    async def get_fact(self, guild_id: int, contents: str):
        """Gets a specific fact (row from psql)"""
        query = '''SELECT * from user_facts
                   WHERE guild_id = $1
                   AND contents = $2;'''

        return await self.pg_con.fetchrow(query, guild_id, contents)

    async def get_random_fact(self, guild_id: int):
        """Returns a random fact"""
        query = '''SELECT * from user_facts
                   WHERE guild_id = $1
                   ORDER BY RANDOM()
                   LIMIT 1;'''

        return await self.pg_con.fetchrow(query, guild_id)

    async def can_delete_fact(self, ctx, contents: str):
        """Check whether the user can delete the fact they want"""
        fact = await self.get_fact(ctx.guild.id, contents)

        if not fact:
            return None

        fact_owner = fact['member_id']

        return ctx.message.channel.permissions_for(ctx.author).administrator or fact_owner == ctx.author.id

    async def total_facts(self, ctx):
        """Check whether a server has any facts"""
        query = '''SELECT COUNT(*) FROM user_facts
                   WHERE guild_id = $1;'''

        return await self.pg_con.fetch(query, ctx.guild.id)

    @commands.group(invoke_without_command=True)
    async def ufact(self, ctx):
        """Get a random user-created fact from your server"""
        # Check to see whether any facts have been created
        # if await self.total_facts(ctx) < 1:
        #     return await ctx.error('Your server does not have any facts set up!',
        #                            description=f'Use the `{self.bot.get_prefix(ctx.message)[-1]}ufact add` command to '
        #                                        'start getting random facts you\'ve created.')
        #
        # fact = await self.get_random_fact(ctx.guild.id)
        # user = ctx.guild.get_member(fact['member_id'])
        # contents = fact['contents']
        #
        # em = discord.Embed(title=':bookmark: Fact.', description=contents, timestamp=fact['created'])
        # em.set_footer(text=f'Created by {user} at', icon_url=user.avatar_url)
        #
        # await ctx.send(embed=em)
        total = await self.total_facts(ctx)
        await ctx.send(str(total))

    @ufact.command(aliases=['create', 'ad'])
    async def add(self, ctx, *, contents: str = None):
        """Add a 100% true™ fact to the database"""
        if contents is None:
            return await ctx.error("Can't add an empty fact boss, sorry!")

        query = '''INSERT INTO user_facts
                   (guild_id, member_id, contents, created)
                   VALUES ($1, $2, $3, now());'''

        try:
            await self.pg_con.execute(query, ctx.guild.id, ctx.author.id, contents)
        except asyncpg.UniqueViolationError:
            return await ctx.error('Sorry, that fact already exists.')

        await ctx.success('Added that fact for ya!')


def setup(bot):
    bot.add_cog(UserFacts(bot))
