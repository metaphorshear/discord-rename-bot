from asyncio import Future
from nextcord.ext import commands
from io import BytesIO
from requests_futures.sessions import FuturesSession
from nextcord import Embed

def temp_url(data):
    with FuturesSession() as sesh:
        req = sesh.put("https://oshi.at/?expire=5&autodestroy=1", data=data)
        resp = req.result()
        if resp.ok:
            fields = resp.text.split()
            return fields[2]
    return