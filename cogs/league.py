#!/bin/env python

import discord
import json
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
        self.elo_api_uri = 'https://na.whatismymmr.com/api/v1/summoner?name={}'
        self.elo_headers = {'user-agent': 'qtbot/1.0'}

        with open('data/apikeys.json') as fp:
            api_keys = json.load(fp)

        self.champion_gg_api_key = api_keys['champion.gg']
        self.riot_api_key = api_keys['riot']
        self.riot_observer = ro(self.riot_api_key)

    @commands.command(name='aln', aliases=['addl', 'addleague'])
    async def add_league_name(self, ctx, *, summoner_name):
        """ Add your summoner name to the user file """
        ufm.update_user_info(str(ctx.author.id), 'summoner_name', summoner_name)
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

        # Try to read summoner from file if none supplied
        if not summoner:
            summoner = ufm.get_user_info(str(ctx.author.id), 'summoner_name')

        # get_user_info() will return None if there is no summoner found
        if summoner is None:
            return await ctx.send("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply a name to this command.")

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
                self.aio_session, self.elo_api_uri.format(f_summoner), headers=self.elo_headers)

            # No data found -- don't bother storing it
            if elo_data is None or 'error' in elo_data :
                return await ctx.send(f"Sorry, I can't find `{summoner}`\nResponse:```{elo_data}```")

            # Store in redis cache
            await self.redis_client.set(f'elo:{f_summoner}', json.dumps(elo_data), ex=7200)


        # Replace 'None' with 0 for error margin because "+/- None" looks bad
        for kind in elo_data:
            if elo_data[kind]['err'] is None:
                elo_data[kind]['err'] = 0

        # Create embed
        em = discord.Embed()
        em.title = summoner
        em.url = f'https://na.whatismymmr.com/{f_summoner}'
        em.set_thumbnail(url=lu.get_summoner_icon(summoner, 'na'))

        # Display ranked MMR
        if elo_data['ranked']['avg']:
            # I'll think of a better way to do this later, but for now, it works
            rank_str = elo_data['ranked']['summary'].split('<b>')[1].split('</b')[0]
            new_str = rank_str.split(' ')
            new_str[0] = new_str[0].capitalize()
            rank_str = ' '.join(new_str)

            # Add to embed field
            em.add_field(name='Approximate rank', value=rank_str)
            em.add_field(name='Ranked MMR',
                value=f"{elo_data['ranked']['avg']}±{elo_data['ranked']['err']}")

        # Display normal MMR
        if elo_data['normal']['avg']:
            em.add_field(name='Normal MMR',
                value=f"{elo_data['normal']['avg']}±{elo_data['normal']['err']}")

        # Display ARAM MMR
        if elo_data['ARAM']['avg']:
            em.add_field(name='ARAM MMR', value=f"{elo_data['ARAM']['avg']}±{elo_data['ARAM']['err']}")

        em.set_footer(text="Powered by WhatIsMyMMR.com and Riot's API.")

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(League(bot))
