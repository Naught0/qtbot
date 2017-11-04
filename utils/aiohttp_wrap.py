#!/bin/env python

import aiohttp


async def aio_get_text(aio_session, url, headers=None):
    async with aio_session.get(url, headers=headers) as r:
        if r.status == 200:
            return await r.text()
        else:
            return None


async def aio_get_json(aio_session, url, headers=None):
    async with aio_session.get(url, headers=headers) as r:
        if r.status == 200:
            return await r.json()
        else:
            return None
