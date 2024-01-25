import discord
import random

from discord.utils import escape_markdown
from discord.ext import commands
from utils import aiohttp_wrap as aw


class RNG(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.aio_session
        self.fact_url = "https://uselessfacts.jsph.pl/random.json?language=en"

    @commands.command(aliases=["facts"])
    async def fact(self, ctx):
        """Get a random fun fact (potentially NSFW)"""
        fact = await aw.aio_get_json(self.session, self.fact_url)

        if not fact:
            return await ctx.send(
                random.choice(
                    [
                        "Sorry, I get nervous in front of crowds",
                        "Oh god, I'm blanking",
                        "Just a second, I'll think of something...",
                        "This is no time for fun or facts.",
                    ]
                )
            )
        # Create embed
        em = discord.Embed(description=escape_markdown(fact["text"]))
        em.set_thumbnail(url="https://i.imgur.com/c36rUx9.png")

        await ctx.send(embed=em)

    @commands.command()
    async def react(self, ctx):
        """Have qtbot react with something inane"""
        # Have to get text because it has the wrong content-type
        word1 = "bites,highs,burns,ruins,humids,leans,quiets,traffics,homes,crashes,trumps,backs,salts,xboxs,closes,records,stops,sevens,pollutes,kills,rents,cleans,extras,boggles,Taylor's,snaps,questions,coffee's,clicks,pops,ticks,maintains,stars,ties,nys,bills,defends,opens,airs,Americans,steals,drinks,yous,businesses,teleys,invents,thanks,students,computers,frees,weathers,vends,severs,allergies,silences,fires,ambers,pushes,screws,smokes,mrs,reds,consumes,let's,classes,makes,draws,lights,butters,celebrates,drives,pulls,toxics,finds,waters,pets,lags,types,environments,grows,builds,moos,tunas,confuses,classifies,births,fails,breaks,emotionals,booms,calls,taxes,burgers,4s,gases,potatoes,pre owns,sends,mows,tickles,lefts,Saharas,nals,unites,camps,roses,shuts down,macs,apples,cheeses,turns,flexes,moves,trucks,necks,swallows,Harry's,flushes,pays,eyes,cities,increases,trains,cooks,i's,cringes,unders,folds,enters,speeds,roads,spends,tacos,pumps,hearts,Willows,reads,suhs,dogs,rocks,cookies,grinds".split(
            ","
        )

        word2 = "bites,voices,rubber,jokes,weather,dabs,time,jams,depots,parties,country,Clinton,fires,grasses,one,door,videos,signs,elevens,air,mood,movie,rooms,roads,brain cells,points,mind,Swifts,chats,vibe,motives,mugs,pens,buttons,sanity,tocks,office,scouts,shoes,keys,nyes,freedom,will to live,force,flags,Gatorade,sprite,tubes,service,phones,wheel,yous,services,labs,tuition,ford,machines,warnings,alert,phone,extinguishers,dexterious,driver,detector,jos,cross,M&Ms,goes,days,pictures,poles,biscuit,75 years,cars,levers,waters,ways out,burgers,dogs,minecraft,emojis,sciences,trees,legos,buildings,cows,fish,conversation,animals,certificates,science classes,hearts,issues,roasted,horns,friends,kings,Gs,birthdays,stations,chips,vehicles,texts,lawns,pickles,lanes,deserts,genes,rocks,states,outs,coffee,reds,computers,books,watches,milk,steaks,teens,wheels,muscles,homes,stops,self,tattoos,food,Potters,toilets,brows,limits,toasts,towers,volume,tracks,wears,bones,oragamies,zones,kills,money,bells,ups,radios,ways,Donald's,springs,elections,walls,corn,dudes,filters,rolls,tongues,gears".split(
            ","
        )

        await ctx.send(f"That really {random.choice(word1)} my {random.choice(word2)}!")


async def setup(bot):
    await bot.add_cog(RNG(bot))
