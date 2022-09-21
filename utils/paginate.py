import discord
import asyncio

from typing import List, Tuple
from discord.ext.commands import Context

EMOJIS = {"back": "⬅️", "forward": "➡️"}
async def paginate(ctx: Context, embeds: List[discord.Embed], timeout=30.0) -> None:
    msg = ctx.message
    current_index = 0
    while True:
        try:
            (reaction, _): Tuple[discord.Reaction]= await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, user: (
                    user == ctx.author and reaction.emoji in EMOJIS.values() and reaction.message.id == msg.id
                ),
            )
        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        if (reaction.emoji == EMOJIS["back"]):
            current_index -= 1
        if (reaction.emoji == EMOJIS["forward"]):
            current_index += 1

        await msg.edit(embed=embeds[current_index])
        await msg.remove_reaction(reaction.emoji, ctx.author)
