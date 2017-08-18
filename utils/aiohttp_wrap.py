#!/bin/env python

import aiohttp


async def aio_get(url: str):
    async with aiohttp.ClientSession() as session:
    async with session.get(url) as r:
        if r.status == 200:
            return r
        else:
            return None
