import json
import random
import re
from datetime import datetime
from typing import Union, Tuple

import discord
from discord.ext import commands
from nltk.corpus import stopwords


class Comics:
    STOPWORDS = set(stopwords.words('english'))
    with open('data/xkcd_comics.json') as f:
        COMICS = json.load(f)
    with open('data/xkcd_blob.json') as f:
        BLOB = json.load(f)

    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session

    def _process_text(self, text: str) -> str:
        stripped_set = set([re.sub('\W+', '', x) for x in text.lower().split()])
        return ' '.join(stripped_set - self.STOPWORDS)

    def _get_best_match(self, input: str) -> Union[Tuple[int, str], None]:
        match_list = []
        input_set = set(input.lower().split())
        for key in self.BLOB:
            strength = len(set(key.split()) & input_set)
            match_list.append((strength, self.BLOB[key]))

        best_match = sorted(match_list, key=lambda x: x[0], reverse=True)[0]
        if best_match[0] == 0:
            return None

        return best_match

    def _comic_to_embed(self, id_tup: tuple):
        if id_tup is None:
            comic = self.COMICS[random.choice(self.COMICS)]
        else:
            comic = self.COMICS[id_tup[1]]

        em = discord.Embed()
        em.title = comic['safe_title']
        em.set_image(url=comic['img'])
        if comic['link'] != '':
            em.url = comic['link']
        em.set_footer(text='Random comic' if id_tup is None else f'Matched with {id_tup[0]} hit(s)')
        em.timestamp = datetime(int(comic['year']),
                            int(comic['month']),
                            int(comic['day']))

        return em

    @commands.command(aliases=['xk'])
    async def xkcd(self, ctx, *, query: str = None):
        """Search for an xkcd, or get a random one"""
        if query is None:
            return await ctx.send(embed=self._comic_to_embed(None))

        stripped_query = self._process_text(query)
        best_match = self._get_best_match(stripped_query)

        return await ctx.send(embed=self._comic_to_embed(best_match))


def setup(bot):
    bot.add_cog(Comics(bot))
