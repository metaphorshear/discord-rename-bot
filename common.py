from asyncio import Future
from nextcord.ext import commands
from io import BytesIO
from requests_futures.sessions import FuturesSession
from nextcord import Embed

def temp_url(url):
    with FuturesSession() as sesh:
        req = sesh.get(url, verify=False) #this isn't even SSL.  yet it throws the error.
        resp = req.result()
        if resp.ok:
            qer = sesh.put("https://oshi.at/?expire=5", data=resp.content)
            pser = qer.result()
            if pser.ok:
                fields = pser.text.split()
                return fields[2]
    return