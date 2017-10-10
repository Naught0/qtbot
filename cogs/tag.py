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
        query = ''' SELECT server_id, owner_id, tag_name, tag_contents, created_at, total_uses 
                    FROM tags WHERE server_id = $1 
                    AND tag_name = $2; '''

        return await self.pg_con.fetchrow(query, server_id, tag_name)

    async def can_delete_tag(self, ctx, tag_name):
        """ Check whether a user is admin or owns the tag """
        tag_record = await self.get_tag(ctx.guild.id, tag_name)
        tag_owner = tag_record['owner_id']

        if not tag_owner:
            return None

        return ctx.message.channel.permissions_for(ctx.author).administrator or tag_owner == ctx.author.id

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, tag_name: str):
        """ Add a tag to the database for later retrieval """
        tag_record = await self.get_tag(ctx.guild.id, tag_name)

        if tag_record:
            await ctx.send(tag_record['tag_contents'])

            # Update usage count
            query = '''UPDATE tags SET total_uses = total_uses + 1 
                        WHERE server_id = $1
                        AND tag_name = lower($2) '''
            await self.pg_con.execute(query, ctx.guild.id, tag_name)

        else:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

    @tag.command(aliases=['add'])
    async def create(self, ctx, tag_name, *, contents):
        """ Create a new tag for later retrieval """
        query = ''' INSERT INTO tags (server_id, owner_id, tag_name, tag_contents, created_at, total_uses)
                    VALUES ($1, $2, lower($3), $4, now(), $5) '''
        try:
            await self.pg_con.execute(query, ctx.guild.id, ctx.author.id, tag_name, contents, 0)
            await ctx.send(f'Tag `{tag_name}` created.')
        except asyncpg.UniqueViolationError:
            return await ctx.send(f'Sorry, tag `{tag_name}` already exists. If you own it, feel free to `.tag edit` it.')

    @tag.command(name='delete', aliases=['del', 'delet'])
    async def _delete(self, ctx, *, tag_name):
        """ Delete a tag you created (or if you're an admin) """
        _can_delete = await self.can_delete_tag(ctx, tag_name)

        if _can_delete is None:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

        elif _can_delete:
            query = "DELETE FROM tags WHERE tag_name = lower($1) AND server_id = $2"
            await self.pg_con.execute(query, tag_name, ctx.guild.id)
            await ctx.send(f'Tag `{tag_name}` deleted.')

        else:
            await ctx.send(f'Sorry, you do not have the necessary permissions to delete this tag.')

    @tag.command(aliases=['ed'])
    async def edit(self, ctx, tag_name, *, contents):
        """ Edit a tag which you created """
        
        # Get the record
        tag_record = await self.get_tag(ctx.guild.id, tag_name)

        # Check whether tag exists
        if not tag_record:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

        # Check owner
        if tag_record['owner_id'] == ctx.author.id:
            query = ''' UPDATE tags SET tag_contents = $1
                        WHERE tag_name = $2
                        AND server_id = $3 '''
            await self.pg_con.execute(query, contents, tag_name, ctx.guild.id)
            await ctx.send(f'Successfully edited tag `{tag_name}`.')

        else:
            await ctx.send(f'Sorry, you do not have the necessary permissions to delete this tag.')

    @tag.command()
    async def info(self, ctx, *, tag_name):
        """ Retrieve information about a tag """

        # Get the record
        tag_record = await self.get_tag(ctx.guild.id, tag_name)

        # Check whether tag exists
        if not tag_record:
            return await ctx.send(f"Sorry, I couldn't find a tag matching `{tag_name}`.")

        # Create the embed
        em = discord.Embed(title=tag_record['tag_name'], color=discord.Color.blue())
        em.timestamp = tag_record['created_at']
        em.set_footer(text='Created at')

        user = self.bot.get_user(tag_record['owner_id']) or (await self.bot.get_user_info(tag_record['owner_id']))
        em.set_author(name=str(user), icon_url=user.avatar_url)

        em.add_field(name='Tag Owner:', value=f"<@{tag_record['owner_id']}>")
        em.add_field(name='Uses:', value=tag_record['total_uses'])

        await ctx.send(embed=em)

    @tag.command()
    async def search(self, ctx, *, query: str):
        """ Search for some matching tags """ 

        if len(query) < 3:
            return await ctx.send("Sorry, you'll have to be more specific.")

        execute = '''SELECT tag_name 
                        FROM tags
                        WHERE server_id = $1 AND tag_name % $2::text
                        ORDER BY similarity(tag_name, $2) DESC
                        LIMIT 10;'''

        search_results = await self.bot.pg_con.fetch(execute, ctx.guild.id, query)

        await ctx.send(search_results)


def setup(bot):
    bot.add_cog(Tag(bot))
