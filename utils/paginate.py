import discord
import asyncio

from typing import List
from discord.ext.commands import Context

EMOJI_MAP = {"back": "⬅️", "forward": "➡️"}


def generate_number_emoji_range(start: int, end: int) -> list[str]:
    """Generate a list of emoji numbers including end"""
    return [f"{n}\U000020e3" for n in range(start, end + 1)]


async def paginate(
    ctx: Context, msg: discord.Message, embeds: List[discord.Embed], timeout=30.0
) -> None:
    """
    Add ⬅️ and ➡️ reactions to a message and let the author paginate through
    a list of embeds by reacting. On a forward reaction the index advances
    (clamped to the last embed); on a back reaction it decrements (clamped
    to 0). The displayed embed is updated on each valid reaction, and the
    user's reaction is removed so it can be pressed again. The loop exits
    when no reaction is received within ``timeout`` seconds, at which point
    all reactions are cleared.

    Example:
        >>> embeds = [
        ...     discord.Embed(title="Page 1", description="First page"),
        ...     discord.Embed(title="Page 2", description="Second page"),
        ...     discord.Embed(title="Page 3", description="Third page"),
        ... ]
        >>> msg = await ctx.send(embed=embeds[0])
        >>> await paginate(ctx, msg, embeds, timeout=60.0)
    """
    emojis = EMOJI_MAP.values()
    for emoji in emojis:
        await msg.add_reaction(emoji)

    current_index = 0
    total = len(embeds)
    embeds[current_index].set_footer(text=f"({current_index + 1}/{total})")
    await msg.edit(embed=embeds[current_index])

    while True:
        try:
            reaction, _ = await ctx.bot.wait_for(
                "reaction_add",
                timeout=timeout,
                check=lambda reaction, user: (
                    user == ctx.author
                    and reaction.emoji in emojis
                    and reaction.message.id == msg.id
                ),
            )
        except asyncio.TimeoutError:
            return await msg.clear_reactions()

        if reaction.emoji == EMOJI_MAP["back"]:
            current_index = current_index - 1 if current_index > 0 else 0
        if reaction.emoji == EMOJI_MAP["forward"]:
            current_index = (
                current_index + 1
                if current_index < len(embeds) - 1
                else len(embeds) - 1
            )

        embeds[current_index].set_footer(text=f"({current_index + 1}/{total})")
        await msg.edit(embed=embeds[current_index])
        await msg.remove_reaction(reaction.emoji, ctx.author)
