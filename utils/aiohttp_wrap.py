#!/bin/env python

import aiohttp

async def aio_get(aio_session, url, headers=None):
    async with aio_session as s:
        async with s.get(url, headers=headers) as r:
            if r.status == 200:
                return await r.text()
            else:
                return None
