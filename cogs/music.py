import discord
from discord.ext import commands

from utils import aiohttp_wrap as aw 


class MusicInfo:
    """A cog for retrieving music information (not playing it)"""
    URL = 'http://ws.audioscrobbler.com/2.0/'
    LOGO_URL = 'https://www.last.fm/static/images/lastfm_logo_facebook.1b63d4451dcc.png'
    TOKEN = self.api_keys['lastfm']
    NO_RESULT = "Sorry, couldn't find anything for {}."
    EM_COLOR = discord.Color.blurple()

    @staticmethod
    def truncat(text: str, length=500) -> str:
        if len(text) > length:
            return f'{text[:length - 3]}...'

        return text

    @commands.group(aliases=['lastfm', 'fm'])
    async def music(self, ctx):
        """Main group cmd"""
        pass

    @music.command()
    async def album(self, ctx, *, query):
        """Search for some basic album information via album name"""
        search_params = {'method': 'album.search', 'album': query, 'limit': 5, 'api_key': self.TOKEN}
        search_resp = await aw.aio_get_json(ctx.bot.aio_session, self.URL, params=search_params)

        # API didn't respond
        if search_resp is None:
            return await ctx.error('There was a problem with the last.fm API, try again later.')

        # No results
        if len(search_resp['results']['albummatches']['album']) == 0:
            return await ctx.error(self.NO_RESULT.format(query))

        search_result = search_resp['results']['albummatches']['album'][0]
        name = search_result['name']
        artist = search_result['artist']

        # Once we've found the matching album, we've gotta do ANOTHER request
        info_params = {'method': 'album.search', 'artist': artist, 'album': name, 'api_key': self.TOKEN}
        info_resp = await aw.aio_get_json(ctx.bot.aio_session, self.URL, params=info_params)

        em = discord.Embed(title=f'{artist} - {name}',
                           url=info_resp['url'],
                           color=self.EM_COLOR)
        em.set_thumbnail(url=info_resp['image'][-1])
        # If there's some wiki info, include it
        if info_resp['wiki']['summary']:
            em.description = self.truncat(info_resp['wiki']['summary'])

        # Get and number the tracks in a list
        tracks = [f"{idx}. {x['name']}" for idx, x in enumerate(info_resp['tracks']['track'])]
        em.add_field(name='Track List', text='\n'.join(tracks))

        # Attribution or whatever
        em.set_footer(text='Powered by last.fm', icon_url=self.LOGO_URL)

        await ctx.send(embed=em)


def setup(bot):
    bot.add_cog(MusicInfo(bot))
