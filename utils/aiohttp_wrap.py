import aiohttp


SUCCESS = 200

async def aio_get_text(aio_session, url, headers = None, params = None):
    async with aio_session.get(url, headers=headers, params=params) as r:
        if r.status == SUCCESS:
            return await r.text()
        else:
            return None


async def aio_get_json(aio_session, url, headers = None, params = None):
    async with aio_session.get(url, headers=headers, params=params) as r:
        if r.status == SUCCESS:
            return await r.json()
        else:
            return None
