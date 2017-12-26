#!/bin/env python

import ast
import json
import textwrap

import discord
import lolrune
from bs4 import BeautifulSoup
from discord.ext import commands
from riot_observer import RiotObserver as ro

from utils import aiohttp_wrap as aw
from utils import dict_manip as dm
from utils import league as lu
from utils.user_funcs import PGDB


class League:
    FORGE_FAVICON_URL = 'http://d181w3hxxigzvh.cloudfront.net/wp-content/themes/rune_forge/favicon-96x96.png'

    def __init__(self, bot, rune_client: lolrune.AioRuneClient = None):
        # Bot attrs
        self.bot = bot
        self.session = bot.aio_session
        self.redis_client = bot.redis_client
        self.db = PGDB(bot.pg_con)

        # Optional RuneClient
        self.rune_client = rune_client or lolrune.AioRuneClient(loop=bot.loop, session=bot.aio_session)

        # Request information
        self.elo_api_uri = 'https://na.whatismymmr.com/api/v1/summoner?name={}'
        self.elo_headers = {'user-agent': 'qtbot/1.0'}
        self.browser_headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                                              'like Gecko) Chrome/64.0.3257.0 Safari/537.36'}
        self.patch_url = 'https://na.leagueoflegends.com/en/news/game-updates/patch'

        # API deets
        with open('data/apikeys.json') as fp:
            api_keys = json.load(fp)

        self.champion_gg_api_key = api_keys['champion.gg']
        self.riot_api_key = api_keys['riot']
        self.riot_observer = ro(self.riot_api_key)

    @commands.command(name='aln', aliases=['addl'])
    async def add_league_name(self, ctx, *, summoner_name):
        """ Add your summoner name to the database """
        await self.db.insert_user_info(ctx.author.id, 'league_name', summoner_name)
        await ctx.send(f'Successfully added `{summoner_name}` for `{ctx.author}`.')

    @commands.command(name='rln')
    async def remove_league_name(self, ctx):
        """ Remove your summoner name from the database """
        await self.db.remove_user_info(ctx.author.id, 'league_name')
        await ctx.send(f'Successfully removed League name for `{ctx.author}`.')

    @commands.command(name='ci', aliases=['champ'])
    async def get_champ_info(self, ctx, *, champ):
        """ Return play, ban, and win rate for a champ """
        uri = 'http://api.champion.gg/v2/champions/{}?sort=playRate-desc&api_key={}'
        icon_uri = 'https://ddragon.leagueoflegends.com/cdn/7.24.1/img/champion/{}.png'

        champ = champ.replace(' ', '')
        riot_champ_name = lu.get_riot_champ_name(champ)
        fancy_champ_name = lu.get_fancy_champ_name(riot_champ_name)
        champ_title = lu.get_champ_title(riot_champ_name)
        champ_id = lu.get_champ_id(riot_champ_name)

        # Check for cached results
        if await self.redis_client.exists(f'champ_info:{champ_id}'):
            res_string = await self.redis_client.get(f'champ_info:{champ_id}')
            res = json.loads(res_string)

        # Stores results if not found in cache for 6hrs (API only updates twice a day anyway)
        else:
            res = await aw.aio_get_json(self.session, uri.format(champ_id, self.champion_gg_api_key))

            # New champs have no data
            if not res:
                return await ctx.send('Sorry, no data for `{}`, yet.'.format(fancy_champ_name))

            await self.redis_client.set(f'champ_info:{champ_id}', json.dumps(res), ex=21600)

        # Create embed
        em = discord.Embed(color=discord.Color.green())
        em.title = '{} "{}"'.format(fancy_champ_name, champ_title)
        em.description = None
        em.add_field(name='Role', value=f'{res[0]["role"].split("_")[0].title()} ({res[0]["percentRolePlayed"]:.2%})')
        em.add_field(name='Play rate', value=f'{res[0]["playRate"]:.2%}')
        em.add_field(name='Win rate', value=f'{res[0]["winRate"]:.2%}')
        em.add_field(name='Ban rate', value=f'{res[0]["banRate"]:.2%}')
        em.set_thumbnail(url=icon_uri.format(riot_champ_name))
        em.url = f'http://champion.gg/champion/{riot_champ_name}'
        em.set_footer(text="Powered by Champion.gg and Riot's API.")

        return await ctx.send(embed=em)

    @commands.command(name='ucf', hidden=True)
    @commands.is_owner()
    async def update_champ_file(self, ctx):
        """ Creates / updates a json file containing champion IDs, names, titles, etc. """

        # Case where champ data found
        if lu.found_champ_file():
            with open('data/champ_data.json') as f:
                file_champ_list = json.load(f)

            # Get champ list from Riot's API
            new_champ_list = await self.bot.loop.run_in_executor(None, ro.static_get_champion_list())

            # If file is up to date, don't update
            if len(new_champ_list['data']) == len(file_champ_list['data']):
                return await ctx.send('Champion information file already up to date.')

            # File needs updating
            else:
                with open('data/champ_data.json', 'w') as f:
                    json.dump(new_champ_list, f)
                return await ctx.send('Champion file updated.')

        # Create champion data file if not found
        else:
            new_champ_list = await self.bot.loop.run_in_executor(None, ro.static_get_champion_list())

            with open('data/champ_data.json', 'w') as f:
                json.dump(new_champ_list, f)

        await ctx.send('Creating chamption information file.')

    @commands.command(name='elo', aliases=['mmr'])
    async def get_league_elo(self, ctx, *, summoner=''):
        """ Get League of Legends elo / mmr from na.whatismymmr.com """
        # WhatIsMyMMR API licensed under Creative Commons Attribution 2.0 Generic
        # More information here: https://creativecommons.org/licenses/by/2.0

        # Try to read summoner from file if none supplied
        if not summoner:
            summoner = await self.db.fetch_user_info(ctx.author.id, 'league_name')

        # fetch_user_info() will return None if there is no summoner found
        if summoner is None:
            return await ctx.send("Sorry you're not in my file. "
                                  "Use `aln` or `addl` to add your League of Legends summoner name, "
                                  "or supply a name to this command.")

        f_summoner = summoner.replace(' ', '%20')

        # Check whether there is a cached elo_dataponse
        if await self.redis_client.exists(f'elo:{f_summoner}'):
            raw_elo_data = await self.redis_client.get(f'elo:{f_summoner}')
            elo_data = json.loads(raw_elo_data)

        # Make the call
        # Store the data for 2hrs because it doesn't update that frequently
        else:
            # Send typing because this can take a while
            await ctx.trigger_typing()
            elo_data = await aw.aio_get_json(
                self.session, self.elo_api_uri.format(f_summoner), headers=self.elo_headers)

            # No data found -- don't bother storing it
            if elo_data is None or 'error' in elo_data:
                return await ctx.send(f"Sorry, I can't find `{summoner}`\nResponse:```{elo_data}```")

            # Store in redis cache
            await self.redis_client.set(f'elo:{f_summoner}', json.dumps(elo_data), ex=2 * 60 * 60)

        # Replace 'None' with 0 for error margin because "+/- None" looks bad
        for kind in elo_data:
            if elo_data[kind]['err'] is None:
                elo_data[kind]['err'] = 0

        # Create embed
        em = discord.Embed(color=discord.Color.green())
        em.title = summoner
        em.url = f'https://na.whatismymmr.com/{f_summoner}'
        em.set_thumbnail(url=lu.get_summoner_icon(f_summoner))

        # Display ranked MMR
        if elo_data['ranked']['avg']:
            # I'll think of a better way to do this later, but for now, it works
            rank_str = elo_data['ranked']['summary'].split('<b>')[1].split('</b')[0]
            new_str = rank_str.split(' ')
            new_str[0] = new_str[0].capitalize()
            rank_str = ' '.join(new_str)

            # Add to embed field
            em.add_field(name='Approximate rank', value=rank_str)
            em.add_field(name='Ranked MMR', value=f"{elo_data['ranked']['avg']}±{elo_data['ranked']['err']}")

        # Display normal MMR
        if elo_data['normal']['avg']:
            em.add_field(name='Normal MMR', value=f"{elo_data['normal']['avg']}±{elo_data['normal']['err']}")

        # Display ARAM MMR
        if elo_data['ARAM']['avg']:
            em.add_field(name='ARAM MMR', value=f"{elo_data['ARAM']['avg']}±{elo_data['ARAM']['err']}")

        em.set_footer(text="Powered by WhatIsMyMMR.com and Riot's API.")

        await ctx.send(embed=em)

    @commands.command(aliases=['patch', 'pnotes'])
    async def patch_notes(self, ctx):
        """ Get the latest League of Legends patch notes """
        if await self.redis_client.exists('league_pnotes'):
            em_dict = ast.literal_eval(await self.redis_client.get('league_pnotes'))
            em = discord.Embed.from_data(em_dict)

        else:
            # Initial request for the newest patch notes
            patch_main_html = await aw.aio_get_text(self.session, self.patch_url, headers=self.browser_headers)
            soup = BeautifulSoup(patch_main_html, 'lxml')
            newest_patch_url = f'https://na.leagueoflegends.com{soup.find("h4").a["href"]}'
            image_url = f"https://na.leagueoflegends.com{soup.find('img', attrs={'typeof': 'foaf:Image'})['src']}"

            # Scrape the actual patch notes page
            patch_page_html = await aw.aio_get_text(self.session, newest_patch_url, headers=self.browser_headers)
            soup = BeautifulSoup(patch_page_html, 'lxml')
            patch_summary = textwrap.shorten(soup.find('blockquote').text, width=1000, placeholder='...')

            # Create embed
            em = discord.Embed(color=discord.Color.green(), url=newest_patch_url, description=patch_summary)
            em.set_image(url=image_url)
            em.set_author(name='LoL Patch Notes',
                          icon_url='http://2.bp.blogspot.com/-HqSOKIIV59A/U8WP4WFW28I/AAAAAAAAT5U/qTSiV9UgvUY/s1600/icon.png')

            # Store this embed for 3 hours for easy retrieval later
            await self.redis_client.set('league_pnotes', str(em.to_dict()), ex=10800)

        await ctx.send(embed=em)

    @commands.command(aliases=['rune'])
    async def runes(self, ctx, *, champion: str):
        """ Get the LoL runes for a particular champion """
        icon_uri = 'https://ddragon.leagueoflegends.com/cdn/7.24.1/img/champion/{}.png'
        if champion not in self.rune_client.rune_links:
            champion = dm.get_closest(self.rune_client.rune_links, champion)

        # TODO:
        # Add pagination
        champ = (await self.rune_client.get_runes(champion))[0]
        runes = champ.runes
        riot_champ_name = lu.get_riot_champ_name(champion)

        # Create the embed
        em = discord.Embed(title=champ.name, color=discord.Color.green())
        em.description = champ.description
        em.set_author(icon_url=self.FORGE_FAVICON_URL)
        em.set_thumbnail(url=icon_uri.format(riot_champ_name))
        primary_runes = runes.primary.runes[:]
        primary_runes.insert(0, runes.keystone)
        em.add_field(name=f'Primary: {runes.primary.name}',
                     value='\n'.join([f'\u2022 {x}' for x in primary_runes]))
        em.add_field(name=f'Secondary: {runes.secondary.name}',
                     value='\n'.join([f'\u2022 {x}' for x in runes.secondary.runes]))

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(League(bot))
