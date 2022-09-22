import discord
import asyncio

from typing import List
from discord.ext.commands import Context

EMOJI_MAP = {"back": "⬅️", "forward": "➡️"}


async def paginate(ctx: Context, embeds: List[discord.Embed], timeout=30.0) -> None:
    msg = ctx.message
    emojis = EMOJI_MAP.values()
    for emoji in emojis:
        await msg.add_reaction(emoji)

    current_index = 0
    while True:
        try:
            reaction, _ = await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, user: (
                    user == ctx.author and reaction.emoji in emojis and reaction.message.id == msg.id
                ),
            )
        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        if reaction.emoji == EMOJI_MAP["back"]:
            current_index = current_index - 1 if current_index > 0 else 0
        if reaction.emoji == EMOJI_MAP["forward"]:
            current_index = current_index + 1 if current_index < len(embeds) - 1 else len(embeds) - 1

        await msg.edit(embed=embeds[current_index])
        await msg.remove_reaction(reaction.emoji, ctx.author)
