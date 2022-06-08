import os
from nextcord.ext import commands
from nextcord.utils import get
from dotenv import load_dotenv
import re
from time import time_ns
from nextcord import Embed, File
from io import BytesIO
import requests
import logging

logging.basicConfig(level=logging.WARNING)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DEST_CHANNEL')
bot = commands.Bot(command_prefix='r!')
unknown = re.compile(r'unknown\.\w{2,4}$')
imagen = re.compile(r'image\d+\.\w{2,4}$')

async def send_to_thread(message):
    threads = message.channel.threads
    send_to = None
    for thread in threads:
        if thread.owner.bot:
            send_to = thread
    if send_to is None:
        send_to = await message.create_thread(name="renamed files", auto_archive_duration=60)
    return send_to
  
async def send_to_channel(guild, channel=CHANNEL):
    ch = get(guild.text_channels, name=channel)
    return ch

async def rename_file(f):
    try:
        if re.search(unknown, f.filename) or re.search(imagen, f.filename):
            f.filename = f"{time_ns()}.{f.filename.split('.')[-1]}"
            fp = await f.to_file(use_cached=True)
            return fp
    except AttributeError:
        if re.search(unknown, f.url) or re.search(imagen, f.url):
            req = requests.get(f.url)
            if req.status_code != 200 and f.image != Embed.Empty:
                req = requests.get(f.proxy_url)
            raw_fp = BytesIO(req.content)
            filename = f"{time_ns()}.{f.url.split('.')[-1]}"
            fp = File(raw_fp, filename=filename)
            return fp  

@bot.listen('on_message')
async def rename(message):
    new_attachments = []
    for f in message.attachments:
        fp = await rename_file(f)
        if fp is not None:
            new_attachments.append(fp)
    for e in message.embeds:
        if e.image != Embed.Empty or e.video != Embed.Empty:
            fp = await rename_file(e)
            if fp is not None:
                new_attachments.append(fp)
    if len(new_attachments) > 0:
        send_to = await send_to_channel(message.guild)
        await send_to.send(files=new_attachments)
 
def check_perms(ctx):
    return ctx.author.guild_permissions.administrator or (ctx.author.id == 437802570962960406)
 
@bot.command
@commands.check(check_perms)
async def reload(ctx, extension: str):
    try:
        bot.reload_extension(extension)
    except commands.ExtensionNotLoaded:
        bot.load_extension(extension)
    except commands.ExtensionNotFound:
        await ctx.send(f"No such extension: {extension}.")
    except commands.ExtensionFailed as e:
        await ctx.send(f"Extension failed.  Exception type is {type(e)}")
    else:
        await ctx.send("Reloaded successfully.")

bot.run(TOKEN)