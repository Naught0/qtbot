#!/bin/env python

import discord
import asyncpg
from datetime import datetime
from discord.ext import commands

class Tag:
    def __init__(self, bot):
       self.bot = bot
       self.pg_con = bot.pg_con

    async def get_tag(self, server_id: int, name: str):
        """ Returns tag value or None """
        query = ''' SELECT tag_contents 
                    FROM tags WHERE server_id = $1 
                    AND tag_name = $2; '''

        return await self.pg_con.fetchval(query, server_id, name)

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
    async def create(self, ctx, name, *, contents):
        """ Create a new tag for later retrieval """
        query = ''' INSERT INTO tags (server_id, owner_id, tag_name, tag_contents, created_at, total_uses)
                    VALUES ($1, $2, $3, lower($4), now(), $5) '''
        try:
            await self.pg_con.execute(query, ctx.guild.id, ctx.author.id, name, contents, 0)
            await ctx.send(f'Tag `{name}` created.')
        except asyncpg.UniqueViolationError:
            return await ctx.send(f'Sorry, tag `{name}` already exists. If you own it, feel free to `.tag edit` it.')

    @tag.command(name='delete', aliases=['del'])
    async def _delete(self, ctx, *, name):
        """ Delete a tag you created (or if you're an admin) """

        # Check for owner of tag & whether tag exists
        query = ''' SELECT owner_id FROM tags WHERE server_id = $1 AND tag_name = $2; '''
        owner_id = await self.pg_con.fetchval(query, ctx.guild.id, name)

        if not owner_id:
            return await ctx.send(f'Tag `{name}` does not exist.')

        if owner_id == ctx.author.id:
            execute = "DELETE FROM tags WHERE tag_name = lower($1) AND server_id = $2"
            await self.pg_con.execute(execute, name, ctx.guild.id)
            await ctx.send(f'Tag `{name}` deleted.')

        else:
            await ctx.send(f'Sorry, you do not have the necssary permissions to delete this tag.')


def setup(bot):
    bot.add_cog(Tag(bot))
