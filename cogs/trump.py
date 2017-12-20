import discord 
import json
import random
import html
from datetime import datetime, timezone
from discord.ext import commands


class Trump:
    """ A cog which nobody ever asked for, that fetches a random Trump tweet """
    with open('data/trump.json', encoding='utf8') as f:
        TRUMP_JSON = json.load(f)
    THUMB_URLS = ('https://i.imgur.com/36idZdn.png',
                 'https://eastscroll.com/wp-content/uploads/2017/02/Donald-Trump-cutout.png',
                 'http://pngimg.com/uploads/donald_trump/donald_trump_PNG20.png',
                 'https://basicgestalt.files.wordpress.com/2017/07/trumphead3.png?w=234&h=333')
    FOOTER_URL = 'http://icons.iconarchive.com/icons/uiconstock/socialmedia/512/Twitter-icon.png'
    TWITTER_STATUS_URL = 'https://twitter.com/statuses/{}'

    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _to_datetime(time: str) -> datetime:
        """ Small helper which converts twitter TZs to a datetime obj 
        
        Relevant SO answer found here 
        https://stackoverflow.com/questions/7703865/going-from-twitter-date-to-python-datetime-date"""
        return datetime.strptime(time, '%a %b %d %H:%M:%S %z %Y').replace(tzinfo=timezone.utc)

    @commands.command(aliases=['tweet', 'twit', 'tt'])
    async def trump(self, ctx):
        """ Get a random Trump tweet """
        icon_url = random.choice(self.THUMB_URLS)
        tweet_json = random.choice(self.TRUMP_JSON)

        # Create the embed
        em = discord.Embed(color=0x00bef5, url=self.TWITTER_STATUS_URL.format(tweet_json['id_str']))
        em.description = html.unescape(tweet_json['text'])
        em.set_author(name='Donald J. Trump \U00002611', icon_url=icon_url)
        em.add_field(name='Retweets', value=tweet_json['retweet_count'])
        em.add_field(name='Likes', value=tweet_json['favorite_count'])
        em.timestamp = self._to_datetime(tweet_json['created_at'])
        em.set_footer(text=tweet_json['source'], icon_url=self.FOOTER_URL)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(Trump(bot))
