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

    # Get API key
    with open("data/apikeys.json", "r") as f:
        api_keys = json.load(f)

    riot_api_key = api_keys["riot"]

    # Get Champion.gg API key
    champion_gg_api_key = api_keys["champion.gg"]

    # Init RiotObserver
    rito = ro(riot_api_key)

    @commands.bot.command(pass_context=True, aliases=['aln', 'addl', 'addleague'])
    async def addLeagueName(self, ctx, *args):
        self.member = str(ctx.message.author)
        self.summoner_name = " ".join(args)

        if not ufm.foundUserFile():
            await self.bot.say("No user file found...\nCreated user file and added `{}'s`' summoner name as `{}`.".format(self.member, self.summoner_name))
            ufm.createUserFile(self.member, "summoner_name",
                               self.summoner_name)
            return
        else:
            await self.bot.say("Added `{}` as summoner name for `{}`.".format(self.summoner_name, self.member))
            ufm.updateUserInfo(self.member, "summoner_name",
                               self.summoner_name)
            return

    @commands.bot.command(aliases=['champ', 'ci'])
    async def getChampInfo(self, *args):
        """ Return play, ban, and win rate for a champ """
        self.uri = "http://api.champion.gg/v2/champions/{}?api_key={}"
        self.champ = " ".join(args)
        self.champID = lu.getChampID(self.champ)
        self.res = requests.get(self.uri.format(
            self.champID, League.champion_gg_api_key)).json()
        self.role = self.res[0]["role"]
        self.role_rate = self.res[0]["percentRolePlayed"]
        self.play_rate = self.res[0]["playRate"]
        self.win_rate = self.res[0]["winRate"]
        self.ban_rate = self.res[0]["banRate"]

        await self.bot.say("Champion.gg stats for `{} - {} ({:.2%} in role)`:\nPlay Rate: `{:.2%}`\nWin Rate: `{:.2%}`\nBan Rate: `{:.2%}`".format(self.champ.title(), self.role.title(), self.role_rate, self.play_rate, self.win_rate, self.ban_rate))

    @commands.bot.command(pass_context=True, aliases=['matches'])
    async def matchHistory(self, ctx):
        """ do not use """
        self.member = str(ctx.message.author)
        self.summoner_name = getUserInfo(self.member, "summoner_name")
        self.summoner_obj = League.getSummonerObj(self.summoner_name)
        return await self.bot.say("Latest match information for {} ({})\n{}".format(self.member, self.summoner_name, League.getLastTenMatches(self.summoner_obj)))

    @commands.bot.command(aliases=['ucf'])
    async def updateChampionFile(self):
        """ Creates / updates a json file containing champion IDs, names, etc """

        # Case where champ data found
        if lu.foundChampFile():
            with open("data/champ_data.json", "r") as f:
                self.file_champ_list = json.load(f)

            # Get champ list from Riot's API
            self.champ_list = League.rito.static_get_champion_list()

            # If file is up to date, don't update
            if len(self.champ_list) == len(self.file_champ_list):
                return await self.bot.say("Champion information file already up to date.")

            # File needs updating
            else:
                with open("data/champ_data.json", "w") as f:
                    json.dump(self.champ_list, f)
                return

        # Create champion data file if not found
        else:
            self.champ_list = League.rito.static_get_champion_list()
            await self.bot.say("Creating chamption information file.")
            with open("data/champ_data.json", "w") as f:
                json.dump(self.champ_list, f)
            return

    @commands.bot.command(pass_context=True, aliases=['elo', 'mmr'])
    async def getLeagueElo(self, ctx, summoner=""):
        """ Get League of Legends elo / mmr from na.whatismymmr.com """

        # WhatIsMyMMR API licensed under Creative Commons Attribution 2.0 Generic
        # More information here: https://creativecommons.org/licenses/by/2.0

        # Requests call information
        uri = "https://na.whatismymmr.com/api/v1/summoner?name={}"
        header = {'user-agent': 'qtbot/1.0'}

        # Get who's calling the function
        self.member = str(ctx.message.author)

        # Cache results for 2hrs
        requests_cache.install_cache(expire_after=3600)

        # Try to read summoner from file if none supplied
        if (summoner == ""):
            try:
                summoner = ufm.getUserInfo(self.member, "summoner_name")
            except KeyError:
                return await self.bot.say("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply the name to this command.")

        # Store results from call
        self.result_json = requests.get(
            uri.format(summoner), headers=header).json()

        # No MMR results found
        if self.result_json["ranked"]["avg"] == None:
            return await self.bot.say("Sorry, I found no ranked data for `{}`".format(summoner))

        self.estimated_rank = self.result_json["ranked"]["summary"].split('<b>')[
            1].split('</b')[0]

        return await self.bot.say("Average MMR for `{}`: `{}±{}`\nApproximate ranking: `{}`".format(summoner, self.result_json["ranked"]["avg"], self.result_json["ranked"]["err"], self.estimated_rank))


def setup(bot):
    bot.add_cog(League(bot))
