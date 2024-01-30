from collections import Counter

import discord
import prisma
from bot import QTBot
from discord.ext import commands
from discord.utils import escape_markdown
from prisma.models import Tag as TagModel
from utils.custom_context import CustomContext
from utils.paginate import generate_number_emoji_range


class Tag(commands.Cog):
    def __init__(self, bot: QTBot):
        self.bot = bot
        self.number_reactions = generate_number_emoji_range(1, 5)

    async def get_tag(self, server_id: int, tag_name: str):
        """Returns tag value or None"""
        return await self.bot.prisma.tag.find_first(
            where={"server_id": server_id, "tag_name": tag_name}
        )

    async def can_delete_tag(self, ctx: commands.Context, tag: TagModel) -> bool | None:
        """Check whether a user is admin or owns the tag"""
        return (
            ctx.message.channel.permissions_for(ctx.author).administrator
            or tag.owner_id == ctx.author.id
        )

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, tag_name: str):
        """Add a tag to the database for later retrieval"""
        tag = await self.get_tag(ctx.guild.id, tag_name)

        if tag:
            await ctx.send(tag.tag_contents)

            await self.bot.prisma.tag.update(
                where={"id": tag.id},
                data={"total_uses": {"increment": 1}},
            )
        else:
            return await ctx.error(
                f"Sorry, I couldn't find a tag matching `{tag_name}`."
            )

    @tag.command(aliases=["add", "new"])
    async def create(self, ctx: CustomContext, tag_name, *, contents):
        """Create a new tag for later retrieval"""
        if len(tag_name) < 2:
            return await ctx.error("Tag name should be at least 3 characters")

        try:
            await self.bot.prisma.tag.create(
                data={
                    "total_uses": 0,
                    "tag_name": tag_name,
                    "tag_contents": contents,
                    "owner_id": ctx.author.id,
                    "server_id": ctx.guild.id,
                }
            )
        except prisma.errors.UniqueViolationError:
            return await ctx.error(
                f"Sorry, tag `{tag_name}` already exists. ",
                description="If you own it, feel free to `qt.tag edit` it.",
            )

    @tag.command(aliases=["del", "d"])
    async def delete(self, ctx, *, tag_name):
        """Delete a tag you created (or if you're an admin)"""
        tag = await self.bot.prisma.tag.find_first(
            where={"tag_name": tag_name, "server_id": ctx.guild.id}
        )
        if tag is None:
            return await ctx.error(f"No tags matching `{escape_markdown(tag_name)}`.")

        can_delete = await self.can_delete_tag(ctx, tag)
        if not can_delete:
            return await ctx.error("You don't have permission to delete this tag.")

        await self.bot.prisma.tag.delete(where={"id": tag.id})
        await ctx.success(f"Tag `{escape_markdown(tag_name)}` deleted.")

    @tag.command(aliases=["ed", "update", "upd"])
    async def edit(self, ctx, tag_name: str, *, contents: str):
        """Edit a tag which you created"""
        tag = await self.get_tag(ctx.guild.id, tag_name)

        if tag is None:
            return await ctx.error(
                f"Sorry, I couldn't find a tag matching `{escape_markdown(tag_name)}`."
            )

        # Check owner
        if tag.owner_id == ctx.author.id:
            await self.bot.prisma.tag.update(
                where={"id": tag.id}, data={"tag_contents": contents}
            )
            await ctx.success(f"Successfully edited tag `{escape_markdown(tag_name)}`.")
        else:
            await ctx.error("You don't have permission to delete this tag.")

    @tag.command()
    async def info(self, ctx, *, tag_name):
        """Retrieve information about a tag"""
        tag = await self.get_tag(ctx.guild.id, tag_name)
        if not tag:
            return await ctx.error(
                f"Sorry, I couldn't find a tag matching `{escape_markdown(tag_name)}`."
            )

        em = discord.Embed(title=tag.tag_name, color=discord.Color.blue())
        em.timestamp = tag.created_at
        em.set_footer(text="Created at")

        user = self.bot.get_user(tag.owner_id) or (
            await self.bot.fetch_user(tag.owner_id)
        )
        em.set_author(name=str(user), icon_url=user.display_avatar.url)

        em.add_field(name="Tag Owner:", value=f"<@{tag.owner_id}>")
        em.add_field(name="Uses:", value=tag.total_uses)

        await ctx.send(embed=em)

    @tag.command(aliases=["s", "ss"])
    async def search(self, ctx, *, query: str):
        """Search for some matching tags"""
        if len(query) < 3:
            return await ctx.error("Query must be at least 3 characters")

        query = """SELECT *
                     FROM tags
                     WHERE server_id = $1 AND (tag_name LIKE $2 OR tag_contents LIKE $2)
                     ORDER BY similarity(tag_name, $2) DESC, similarity(tag_contents, $2) DESC
                     LIMIT 10;"""
        search_results = await self.bot.prisma.query_raw(
            query, ctx.guild.id, f"%{query}%", model=TagModel
        )

        em = discord.Embed(title=":mag: Tag Search Results", color=discord.Color.blue())

        if len(search_results) == 1:
            description_strings = ["I found 1 similar tag:"]
        elif len(search_results) > 1:
            description_strings = [f"I found {len(search_results)} similar tags:"]
        else:
            description_strings = [
                f":warning: I could not find any matching tags for `{query}`."
            ]

        for idx, record in enumerate(search_results):
            description_strings.append(
                f"{self.number_reactions[idx]} {record.tag_name}"
            )

        em.description = "\n".join(description_strings)

        await ctx.send(embed=em)

    @tag.command(aliases=["stat"])
    async def stats(self, ctx: commands.Context):
        """Get stats about the tags for your guild"""
        em = discord.Embed(title="Tag Statistics", color=discord.Color.blue())
        em.set_author(
            name=f"{ctx.guild.name}",
            icon_url=ctx.guild.icon.url if ctx.guild.icon else None,
        )

        all_tags = await self.bot.prisma.tag.find_many(
            where={"server_id": ctx.guild.id}
        )
        total_tags = len(all_tags)
        total_tag_uses = sum(t.total_uses for t in all_tags)

        em.description = f"Total Tags: {total_tags}\nTotal Tag Uses: {total_tag_uses}"

        top_tags = sorted(all_tags, key=lambda t: t.total_uses, reverse=True)[:4]
        tag_use_counts = []

        for idx, record in enumerate(top_tags):
            tag_use_counts.append(
                f"{self.number_reactions[idx]} {record.tag_name} ({record.total_uses} uses)"
            )

        em.add_field(name="Most Used Tags", value="\n".join(tag_use_counts))

        top_taggers = Counter(t.owner_id for t in all_tags).most_common(5)
        top_taggers_counts = []

        for idx, record in enumerate(top_taggers):
            top_taggers_counts.append(
                f"{self.number_reactions[idx]} <@{record[0]}> ({record[1]} tags created)"
            )

        em.add_field(name="Top Taggers", value="\n".join(top_taggers_counts))

        await ctx.send(embed=em)


async def setup(bot):
    await bot.add_cog(Tag(bot))
