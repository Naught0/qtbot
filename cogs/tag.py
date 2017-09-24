#!/bin/env python

import discord
import asyncpg
from datetime import datetime
from discord.ext import commands

class Tag:
    def __init__(self, bot):
       self.bot = bot
       self.pg_con = bot.pg_con

    async def get_tag(self, server_id: int, tag_name: str):
        """ Returns tag value or None """
        query = ''' SELECT tag_contents 
                    FROM tags WHERE server_id = $1 
                    AND tag_name = $2; '''

        return await self.pg_con.fetchval(query, server_id, tag_name)

    async def get_tag_owner(self, ctx, tag_name):
        query = ''' SELECT owner_id FROM tags WHERE server_id = $1 AND tag_name = $2; '''
        return await self.pg_con.fetchval(query, ctx.guild.id, tag_name)

    async def can_delete_tag(self, ctx, tag_name):
        """ Check whether a user is admin or owns the tag """
        tag_owner = await self.get_tag_owner(ctx, tag_name)

        if not tag_owner:
            return None

        return ctx.message.channel.permissions_for(ctx.author).administrator or tag_owner == ctx.author.id

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, tag_name: str):
        """ Add a tag to the database for later retrieval """
        tag_contents = await self.get_tag(ctx.guild.id, tag_name)
        if tag_contents:
            await ctx.send(tag_contents)

            # Update usage count
            query = ''' UPDATE tags SET total_uses = total_uses + 1 
                        WHERE server_id = $1
                        AND tag_name = $2 '''
            await self.pg_con.execute(query, ctx.guild.id, tag_name)

        else:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

    @tag.command(aliases=['add'])
    async def create(self, ctx, tag_name, *, contents):
        """ Create a new tag for later retrieval """
        query = ''' INSERT INTO tags (server_id, owner_id, tag_name, tag_contents, created_at, total_uses)
                    VALUES ($1, $2, $3, lower($4), now(), $5) '''
        try:
            await self.pg_con.execute(query, ctx.guild.id, ctx.author.id, tag_name, contents, 0)
            await ctx.send(f'Tag `{tag_name}` created.')
        except asyncpg.UniqueViolationError:
            return await ctx.send(f'Sorry, tag `{tag_name}` already exists. If you own it, feel free to `.tag edit` it.')

    @tag.command(name='delete', aliases=['del'])
    async def _delete(self, ctx, *, tag_name):
        """ Delete a tag you created (or if you're an admin) """
        _can_delete = await self.can_delete_tag(ctx, tag_name)

        if _can_delete is None:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

        elif _can_delete:
            execute = "DELETE FROM tags WHERE tag_name = lower($1) AND server_id = $2"
            await self.pg_con.execute(execute, tag_name, ctx.guild.id)
            await ctx.send(f'Tag `{tag_name}` deleted.')

        else:
            await ctx.send(f'Sorry, you do not have the necssary permissions to delete this tag.')


def setup(bot):
    bot.add_cog(Tag(bot))
