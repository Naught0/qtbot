import discord, requests, json, requests_cache
from discord.ext import commands
from cogs.utils import UserFileManip as ufm

# Get API key
with open("data/apikeys.json", "r") as f:
    api_keys = json.load(f)
riot_api_key = api_keys["riot"]

class League():
    def __init__(self, bot):
        self.bot = bot

    def getSummonerObj(summoner_name):
        return riot.get_summoner_by_name(summoner_name)

    def getLastTenMatches(summoner):
        """ Do not use """ 
        game_type_list = []
        for match in summoner.match_list(num_matches = 10):
            game_type_list.append(match.Stats.win)
        return game_type_list

    @commands.bot.command(pass_context = True, aliases = ['aln', 'addl', 'addleague'])
    async def addLeagueName(self, ctx, *args):
        self.member = str(ctx.message.author)
        self.summoner_name = " ".join(args)

        if not ufm.foundUserFile():
            await self.bot.say("No user file found...\nCreated user file and added `{}'s`' summoner name as `{}`.".format(self.member, self.summoner_name))
            ufm.createUserFile(self.member, "summoner_name", self.summoner_name)
            return
        else:
            await self.bot.say("Added `{}` as summoner name for `{}`.".format(self.summoner_name, self.member))
            ufm.updateUserInfo(self.member, "summoner_name", self.summoner_name)
            return  

    @commands.bot.command(pass_context = True, aliases = ['matches'])
    async def matchHistory(self, ctx):
        """ do not use """ 
        self.member = str(ctx.message.author)
        self.summoner_name = ufm.getUserInfo(self.member, "summoner_name")
        self.summoner_obj= League.getSummonerObj(self.summoner_name)
        return await self.bot.say("Latest match information for {} ({})\n{}".format(self.member, self.summoner_name, League.getLastTenMatches(self.summoner_obj)))

    @commands.bot.command(pass_context = True, aliases = ['elo', 'mmr'])
    async def getLeagueElo(self, ctx, summoner = ""):
        """ Get League of Legends elo / mmr from na.whatismymmr.com """
    
        # WhatIsMyMMR API licensed under Creative Commons Attribution 2.0 Generic
        # More information here: https://creativecommons.org/licenses/by/2.0
        # Requests call information
        uri = "https://na.whatismymmr.com/api/v1/summoner?name={}"
        header = {'user-agent' : 'qtbot/1.0'}

        # Get who's calling the function
        self.member = str(ctx.message.author)

        # Cache results for 1hr 
        requests_cache.install_cache(expire_after = 3600)

        # Try to read summoner from file if none supplied   
        if (summoner == ""):
            try:
                summoner = ufm.getUserInfo(self.member, "summoner_name")
            except KeyError:
                return await self.bot.say("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply the name to this command.")

        # Store results from call
        self.result_json = requests.get(uri.format(summoner), headers = header).json()
        self.estimated_rank = self.result_json["ranked"]["summary"].split('<b>')[1].split('</b')[0]

        return await self.bot.say("Average MMR for `{}`: `{}+/-{}`\nApproximate ranking: `{}`".format(summoner, self.result_json["ranked"]["avg"], self.result_json["ranked"]["err"], self.estimated_rank))

def setup(bot): 
    bot.add_cog(League(bot))