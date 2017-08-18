#!/bin/env python

import aiohttp


async def aio_get_text(url, headers=None):
    async with aiohttp.ClientSession() as session:
        if headers:
            async with session.get(url, headers=headers) as r:
                if r.status == 200:
                    return r.text()
                else:
                    return None
        else:
            async with session.get(url) as r:
                if r.status == 200:
                    return r.text()
                else:
                    return None

async def aio_get_json(url, headers=None):
    async with aiohttp.ClientSession() as session:
        if headers:
            async with session.get(url, headers=headers) as r:
                if r.status == 200:
                    return r.json()
                else:
                    return None
        else:
            async with session.get(url) as r:
                if r.status == 200:
                    return r.json()
                else:
                    return None
