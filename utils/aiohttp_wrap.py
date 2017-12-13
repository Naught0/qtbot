import aiohttp


async def aio_get_text(session: aiohttp.ClientSession, url: str, headers: dict = None, params: dict = None):
    async with session.get(url, headers=headers, params=params) as r:
        if r.status == 200:
            return await r.text()
        else:
            return None


async def aio_get_json(session, url, headers=None, params=None):
    async with session.get(url, headers=headers, params=params) as r:
        if r.status == 200:
            return await r.json()
        else:
            return None

async def session_get(session: aiohttp.ClientSession, *args, **kwargs):
    """ A revamped helper function to reduce aiohttp boilerplate """
    async with session.get(*args, **kwargs) as r:
        if r.status == 200:
            return r 
        else:
            return None
