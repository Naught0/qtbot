#!/bin/env python

import discord
import json
import requests
import requests_cache
from utils import aiohttp_wrap as aw
from discord.ext import commands
from riot_observer import RiotObserver as ro
from utils import user_funcs as ufm
from utils import league as lu


class League:
    def __init__(self, bot):
        self.bot = bot
        self.aio_session = bot.aio_session
        self.redis_client = bot.redis_client

        with open('data/apikeys.json') as f:
            self.riot_api_key = json.load(f)['riot']
            self.champion_gg_api_key = json.load(f)['champion.gg']

        self.riot_observer = ro(api_keys['riot'])


    @commands.command(name='aln', aliases=['addl', 'addleague'])
    async def add_league_name(self, ctx, *, summoner_name):
        """ Add your summoner name to the user file """
        if not ufm.found_user_file():
            ufm.create_user_file(ctx.author.id, 'summoner_name', summoner_name)
            await ctx.send(f"No user file found...\nCreated user file and added `{summoner_name}`.")
        else:
            ufm.update_user_info(ctx.author.id, 'summoner_name', summoner_name)
            await ctx.send(f'Added `{summoner_name}`.')

    @commands.command(name='ci', aliases=['champ'])
    async def get_champ_info(self, ctx, *, champ):
        """ Return play, ban, and win rate for a champ """
        uri = 'http://api.champion.gg/v2/champions/{}?sort=playRate-desc&api_key={}'
        icon_uri = 'https://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{}.png'

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
            res = await aw.aio_get_json(self.aio_session, uri.format(champ_id, self.champion_gg_api_key))

            # New champs have no data
            if not res:
                return await ctx.send('Sorry, no data for `{}`, yet.'.format(fancy_champ_name))

            await self.redis_client.set(f'champ_info:{champ_id}', json.dumps(res), ex=21600)

        # Create embed
        em = discord.Embed()
        em.title = '{} "{}"'.format(fancy_champ_name, champ_title)
        em.description = None
        em.add_field(name='Role',
                     value='{} ({:.2%})'.format(
                         res[0]['role'].split('_')[0].title(), res[0]['percentRolePlayed']))
        em.add_field(name='Play rate',
                     value='{:.2%}'.format(res[0]['playRate']))
        em.add_field(name='Win rate',
                     value='{:.2%}'.format(res[0]['winRate']))
        em.add_field(name='Ban rate',
                     value='{:.2%}'.format(res[0]['banRate']))
        em.set_thumbnail(url=icon_uri.format(riot_champ_name))
        em.url = 'http://champion.gg/champion/{}'.format(riot_champ_name)
        em.set_footer(text="Powered by Champion.gg and Riot's API.")

        return await ctx.send(embed=em)

    @commands.command(name='ucf')
    @commands.is_owner()
    async def update_champ_file(self, ctx):
        """ Creates / updates a json file containing champion IDs, names, titles, etc. """

        # Case where champ data found
        if lu.found_champ_file():
            with open('data/champ_data.json') as f:
                file_champ_list = json.load(f)

            # Get champ list from Riot's API
            new_champ_list = self.riot_observer.static_get_champion_list()

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
            new_champ_list = self.riot_observer.static_get_champion_list()
            with open('data/champ_data.json', 'w') as f:
                json.dump(new_champ_list, f)

        await ctx.send('Creating chamption information file.')

    @commands.command(name='elo', aliases=['mmr'])
    async def get_league_elo(self, ctx, *, summoner=''):
        """ Get League of Legends elo / mmr from na.whatismymmr.com """
        # WhatIsMyMMR API licensed under Creative Commons Attribution 2.0 Generic
        # More information here: https://creativecommons.org/licenses/by/2.0

        # Get who's calling the function
        member = str(ctx.message.author)

        # Try to read summoner from file if none supplied
        if not summoner:
            summoner = ufm.get_user_info(member, 'summoner_name')

        # get_user_info() will return None if there is no summoner found
        if summoner is None:
            return await ctx.send("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply a name to this command.")

        # TODO: remove this final instance of requests
        # Cache results for 2hrs
        requests_cache.install_cache(expire_after=3600)

        # Send typing b/c this can take some time
        await ctx.trigger_typing()

        # Requests call information
        site_uri = 'https://na.whatismymmr.com/{}'
        api_uri = 'https://na.whatismymmr.com/api/v1/summoner?name={}'
        headers = {'user-agent': 'qtbot/1.0'}

        # Store results from call
        f_summoner = summoner.replace(' ', '%20')
        res = requests.get(
            api_uri.format(f_summoner), headers=headers).json()

        # No data found
        if 'error' in res:
            return await ctx.send(f"Sorry, I can't find `{summoner}`")

        # Replace 'None' with 0 for error margin because "+/- None" looks bad
        for kind in res:
            if res[kind]['err'] is None:
                res[kind]['err'] = 0

        # Create embed
        em = discord.Embed()
        em.title = summoner
        em.url = site_uri.format(f_summoner)
        em.set_thumbnail(url=lu.get_summoner_icon(summoner, 'na'))

        # Display ranked MMR
        if res['ranked']['avg']:
            # I'll think of a better way to do this later, but for now, it works
            rank_str = res['ranked']['summary'].split('<b>')[1].split('</b')[0]
            new_str = rank_str.split(' ')
            new_str[0] = new_str[0].capitalize()
            rank_str = ' '.join(new_str)

            # Add to embed field
            em.add_field(name='Approximate rank', value=rank_str)
            em.add_field(name='Ranked MMR',
                value=f"{res['ranked']['avg']}±{res['ranked']['err']}")

        # Display normal MMR
        if res['normal']['avg']:
            em.add_field(name='Normal MMR',
                value=f"{res['normal']['avg']}±{res['normal']['err']}")

        # Display ARAM MMR
        if res['ARAM']['avg']:
            em.add_field(name='ARAM MMR', value=f"{res['ARAM']['avg']}±{res['ARAM']['err']}")

        em.set_footer(text="Powered by WhatIsMyMMR.com and Riot's API.")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(League(bot))
