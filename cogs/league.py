#!/bin/env python

import discord
import requests
import json
import requests_cache
from discord.ext import commands
from pathlib import Path
from riot_observer import RiotObserver as ro
from cogs.utils import LeagueUtils as lu
from cogs.utils import UserFileManip as ufm
from cogs.utils import DictManip as dm


class League():
    def __init__(self, bot):
        self.bot = bot

    # Get API keys
    with open("data/apikeys.json", "r") as f:
        api_keys = json.load(f)

    # Riot API key
    riot_api_key = api_keys["riot"]

    # Champion.gg API key
    champion_gg_api_key = api_keys["champion.gg"]

    # Init RiotObserver
    rito = ro(riot_api_key)

    @commands.bot.command(pass_context=True, aliases=['aln', 'addl', 'addleague'])
    async def addLeagueName(self, ctx, *args):
        member = str(ctx.message.author)
        summoner_name = " ".join(args)

        if not ufm.foundUserFile():
            await self.bot.say("No user file found...\nCreated user file and added `{}'s`' summoner name as `{}`.".format(member, summoner_name))
            ufm.createUserFile(member, "summoner_name",
                               summoner_name)
            return
        else:
            await self.bot.say("Added `{}` as summoner name for `{}`.".format(summoner_name, member))
            ufm.updateUserInfo(member, "summoner_name",
                               summoner_name)
            return

    @commands.bot.command(aliases=['champ', 'ci'])
    async def getChampInfo(self, *args):
        """ Return play, ban, and win rate for a champ """
        uri = "http://api.champion.gg/v2/champions/{}?api_key={}"
        icon_uri = "https://ddragon.leagueoflegends.com/cdn/6.24.1/img/champion/{}.png"

        champ = "".join(args)
        riot_champ_name = lu.get_riot_champ_name(champ)
        fancy_champ_name = lu.get_fancy_champ_name(riot_champ_name)
        champ_title = lu.get_champ_title(riot_champ_name)
        champID = lu.getChampID(riot_champ_name)

        res = requests.get(uri.format(
            champID, League.champion_gg_api_key)).json()

        # New champs have no data
        if not res:
            return await self.bot.say("Sorry, no data for `{}`, yet.".format(fancy_champ_name))

        # Create embed
        em = discord.Embed()
        em.title = '{} "{}"'.format(fancy_champ_name, champ_title)
        em.description = None
        em.add_field(name="Role",
                     value="{} ({:.2%})".format(
                         res[-1]["role"].split("_")[0].title(), res[-1]["percentRolePlayed"]))
        em.add_field(name="Play rate",
                     value="{:.2%}".format(res[-1]["playRate"]))
        em.add_field(name="Win rate",
                     value="{:.2%}".format(res[-1]["winRate"]))
        em.add_field(name="Ban rate",
                     value="{:.2%}".format(res[-1]["banRate"]))
        em.set_thumbnail(url=icon_uri.format(riot_champ_name))
        em.url = "http://champion.gg/champion/{}".format(riot_champ_name)
        em.set_footer(text="Powered by Champion.gg and Riot's API.")

        return await self.bot.say(embed=em)

    # @commands.bot.command(pass_context=True, aliases=['matches'])
    # async def matchHistory(self, ctx):
    #     """ do not use """
    #     member = str(ctx.message.author)
    #     summoner_name = ufm.getUserInfo(member, "summoner_name")
    #     summoner_obj = League.getSummonerObj(summoner_name)
    #     return await self.bot.say("Latest match information for {} ({})\n{}".format(member, summoner_name, League.getLastTenMatches(summoner_obj)))

    @commands.bot.command(aliases=['ucf'])
    async def updateChampionFile(self):
        """ Creates / updates a json file containing champion IDs, names, titles, etc. """

        # Case where champ data found
        if lu.foundChampFile():
            with open("data/champ_data.json", "r") as f:
                file_champ_list = json.load(f)

            # Get champ list from Riot's API
            new_champ_list = League.rito.static_get_champion_list()

            # If file is up to date, don't update
            if len(new_champ_list["data"]) == len(file_champ_list["data"]):
                return await self.bot.say("Champion information file already up to date.")

            # File needs updating
            else:
                with open("data/champ_data.json", "w") as f:
                    json.dump(new_champ_list, f)
                return await self.bot.say("Champion file updated.")

        # Create champion data file if not found
        else:
            new_champ_list = League.rito.static_get_champion_list()
            with open("data/champ_data.json", "w") as f:
                json.dump(new_champ_list, f)
            return await self.bot.say("Creating chamption information file.")

    @commands.bot.command(pass_context=True, aliases=['elo', 'mmr'])
    async def getLeagueElo(self, ctx, *args):
        """ Get League of Legends elo / mmr from na.whatismymmr.com """

        # WhatIsMyMMR API licensed under Creative Commons Attribution 2.0 Generic
        # More information here: https://creativecommons.org/licenses/by/2.0

        summoner = "%20".join(args)
        f_summoner = " ".join(args).title()

        # Requests call information
        site_uri = "https://na.whatismymmr.com/{}"
        uri = "https://na.whatismymmr.com/api/v1/summoner?name={}"
        header = {'user-agent': 'qtbot/1.0'}

        # Get who's calling the function
        member = str(ctx.message.author)

        # Cache results for 2hrs
        requests_cache.install_cache(expire_after=3600)

        # Try to read summoner from file if none supplied
        if (summoner == ""):
            try:
                summoner = f_summoner = ufm.getUserInfo(
                    member, "summoner_name")
            except KeyError:
                return await self.bot.say("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply the name to this command.")

        # Store results from call
        res = requests.get(
            uri.format(summoner), headers=header).json()

        # No data found
        if "error" in res:
            return await self.bot.say("Sorry, I can't find `{}`".format(summoner))

        # Replace "None" with 0 for error margin
        for kind in res:
            if res[kind]["err"] is None:
                res[kind]["err"] = 0

        # Create embed
        em = discord.Embed()

        em.title = f_summoner
        em.url = site_uri.format(summoner)
        em.set_thumbnail(url=lu.get_summoner_icon(summoner, "na"))

        # Display ranked MMR
        if res["ranked"]["avg"] is not None:
            em.add_field(name="Approximate rank", value=res["ranked"]["summary"].split('<b>')[1].split('</b')[0].title())
            em.add_field(name="Ranked MMR", value="{}±{}".format(
                res["ranked"]["avg"], res["ranked"]["err"]))

        # Display normal MMR
        if res["normal"]["avg"] is not None:
            em.add_field(name="Normal MMR", value="{}±{}".format(
                res["normal"]["avg"], res["normal"]["err"]))

        # Display ARAM MMR
        if res["ARAM"]["avg"] is not None:
            em.add_field(name="ARAM MMR", value="{}±{}".format(
                res["ARAM"]["avg"], res["ARAM"]["err"]))

        em.set_footer(text="Powered by WhatIsMyMMR.com and Riot's API.")

        return await self.bot.say(embed=em)


def setup(bot):
    bot.add_cog(League(bot))
