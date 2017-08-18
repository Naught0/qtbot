#!/bin/env python

import aiohttp
import json


async def aio_get_text(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if r.status == 200:
                return await r.text()
            else:
                return None

async def aio_get_json(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as r:
            if r.status == 200:
                return await r.json()
            else:
                return None
