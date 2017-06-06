import discord, requests, json
from discord.ext import commands
from cogs.utils import UserFileManip as ufm
from bs4 import BeautifulSoup # Unfortunate I'm using this
import cassiopeia.riotapi as riot

"""
 __          __           _      _                                                        
 \ \        / /          | |    (_)                                                       
  \ \  /\  / /___   _ __ | | __  _  _ __    _ __   _ __  ___    __ _  _ __  ___  ___  ___ 
   \ \/  \/ // _ \ | '__|| |/ / | || '_ \  | '_ \ | '__|/ _ \  / _` || '__|/ _ \/ __|/ __|
    \  /\  /| (_) || |   |   <  | || | | | | |_) || |  | (_) || (_| || |  |  __/\__ \\__ \
     \/  \/  \___/ |_|   |_|\_\ |_||_| |_| | .__/ |_|   \___/  \__, ||_|   \___||___/|___/
                                           | |                  __/ |                     
  _____   _                               _|_|                 |___/                      
 |  __ \ | |                             | |                      | |                     
 | |__) || |  ___   __ _  ___   ___    __| |  ___    _ __    ___  | |_   _   _  ___   ___ 
 |  ___/ | | / _ \ / _` |/ __| / _ \  / _` | / _ \  | '_ \  / _ \ | __| | | | |/ __| / _ \
 | |     | ||  __/| (_| |\__ \|  __/ | (_| || (_) | | | | || (_) || |_  | |_| |\__ \|  __/
 |_|     |_| \___| \__,_||___/ \___|  \__,_| \___/  |_| |_| \___/  \__|  \__,_||___/ \___|
                                                                                          
"""
# Set Region and API key
with open("data/apikeys.json", "r") as f:
	api_keys = json.load(f)
riot.set_region("NA")
riot.set_api_key(api_keys["riot"])

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
		uri = "https://na.whatismymmr.com/{}"
		self.member = str(ctx.message.author)
		if (summoner == ""):
			try:
				summoner = ufm.getUserInfo(self.member, "summoner_name")
			except KeyError:
				return await self.bot.say("Sorry you're not in my file. Use `aln` or `addl` to add your League of Legends summoner name, or supply the name to this command.")

		# Hideous Soup stuff
		self.req = requests.get(uri.format(summoner))
		self.soup = BeautifulSoup(self.req.text, "lxml")
		self.output = self.soup.findAll('span', {'class' : 'text--main--display'}).text
		return await self.bot.say("I found:\n`{}`".format(self.output))

def setup(bot):	
	bot.add_cog(League(bot))