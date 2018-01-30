import ast
import discord

from typing import List

from lxml import etree
from discord.ext import commands
from bs4 import BeautifulSoup
from utils import aiohttp_wrap as aw


class Google:
    BING_URI = 'https://wwww.bing.com/images/search'
    BING_H = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/4.0; GTB7.4; '
                                 'InfoPath.1; SV1; .NET CLR 2.8.52393; WOW64; en-US)'}
    EMOJIS = [f'{x}\U000020e3' for x in range(1,10)]

    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client
        self.scrape_uri = 'http://www.ask.com/web?q={}&o=0&qo=homepageSearchBox'
        self.headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                                      'Chrome/41.0.2228.0 Safari/537.36'}

    @staticmethod
    def _get_ask_links(html):
        """ Gets all result links from [REDACTED] """
        soup = BeautifulSoup(html, 'lxml')

        link_list = []

        for link in soup.find_all('a', {'class': 'result-link'}, href=True):
            if not link['href'].startswith('//'):
                link_list.append(link['href'])

        return link_list or None

    @commands.group(invoke_without_command=True, name='ask', aliases=['g'])
    async def ask_search(self, ctx, *query):
        """ Get search results from [REDACTED], now that Google hates me. """

        # Handle no input
        if not query:
            return await ctx.send('Feel free to search something.')

        # Format query for search url
        search_query = '+'.join(query)

        # Check if this has been searched in the cache
        if await self.redis_client.exists(f'ask:{search_query}'):
            link_list_str = await self.redis_client.get(f'ask:{search_query}')
            link_list = ast.literal_eval(link_list_str)

        # Actually request page html and store the link list for 6 hrs
        else:
            resp_html = await aw.aio_get_text(self.aio_session, self.scrape_uri.format(search_query), headers=self.headers)
            link_list = self._get_ask_links(resp_html)

            if link_list:
                await self.redis_client.set(f'ask:{search_query}', f'{link_list}', ex=21600)
            else:
                return await ctx.send(f"Sorry, I couldn't find anything for `{query}``.")

        if len(link_list) >= 3:
            await ctx.send(f'**Top result:**\n{link_list[0]}\n**See Also:**\n1. <{link_list[1]}>\n2. <{link_list[2]}>')
        elif len(link_list) >= 2:
            await ctx.send(f'**Top result:**\n{link_list[0]}\n**See Also:**\n1. <{link_list[1]}>')
        else:
            await ctx.send(f'**Top result:**\n{link_list[0]}')

    def _make_image_embed(self, query: str, html: str) -> List[discord.Embed]:
        """Helper method to create a list of embeds of the image results"""
        root = etree.fromstring(html, etree.HTMLParser())
        link_list = [x.get('href') for x in root.xpath('//div[@class="content"]//a[@class="thumb"]')]

        em_dict = {}
        for idx, link in enumerate(link_list[:5]):
            em = discord.Embed(title=f'Results for: `{query}`')
            em.set_image(url=link)
            em_dict[self.EMOJIS[idx]] = em

        return em_dict

    @ask_search.command(name='images', aliases=['-i'])
    async def bing_image_search(self, ctx, *, query):
        """Search for some fantastic imagery my guy"""
        # No input
        if not query:
            return await ctx.send('You have to actually search for something.')

        params = {'q': query}
        html = await aw.aio_get_text(self.aio_session, self.BING_URI, params=params, headers=self.BING_H)
        em_dict = self._make_image_embed(query, html)

        await ctx.send(embed=em_dict[0])


def setup(bot):
    bot.add_cog(Google(bot))
