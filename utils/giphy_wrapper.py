import re
import utils.aiohttp_wrap as aw

async def rand_search(aiohttp_session, query: str="") -> dict:
    if query:
        stripped_query = re.sub('[^A-Za-z0-9 ]+', '', query).replace(' ', '%20')
        api_url = f'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC&tag={stripped_query}'
    else:
        api_url = 'http://api.giphy.com/v1/gifs/random?api_key=dc6zaTOxFJmzC'

    response = await aw.aio_get_json(aiohttp_session, api_url)
    return response['data']
