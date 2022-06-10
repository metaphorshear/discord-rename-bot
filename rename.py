from asyncio import Future
from datetime import timedelta
import os
from nextcord.utils import get, utcnow
from dotenv import load_dotenv
import re
from time import time_ns
from nextcord import Embed, File, Intents, Forbidden, HTTPException
from common import *
import logging

logging.basicConfig(level=logging.WARN)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('DEST_CHANNEL')

intents = Intents.default()
intents.message_content = True
intents.presences = False
intents.typing = False

help = commands.DefaultHelpCommand(no_category="General Commands")
bot = commands.Bot(command_prefix='r!', intents=intents, help_command=help)


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
        try:
            if re.search(unknown, f.url) or re.search(imagen, f.url):
                sesh = FuturesSession()
                req = sesh.get(f.url)
                res = req.result()
                if res.status_code != 200 and f.image != Embed.Empty:
                    req = sesh.get(f.proxy_url)
                    res = req.result()
                raw_fp = BytesIO(res.content)
                filename = f"{time_ns()}.{f.url.split('.')[-1]}"
                fp = File(raw_fp, filename=filename)
                return fp  
        except TypeError:
            pass

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
 
@bot.command()
async def ago(ctx, num: int, unit: str, *channels: str):
    """
    Rename images from the past (if they were unknown or image#).
    Specify the number, unit, and channel(s).  E.g., `r!ago 2 days general nsfw`.
    Supported units are `weeks`, `days`, and `hours`.
    """
    scold = "I don't think you should go back more than three weeks."
    limits = {"weeks": 3, "week": 3, "days": 21, "day": 21, "hours": 504, "hour": 504}
    if unit not in limits:
        await ctx.send("Supported units are `weeks`, `days`, and `hours`.")
        return
    if unit in ["hours", "hour"] and num > limits[unit]:
        await ctx.send(scold + '\n' +
        "Honestly, I should limit you to 72 hours.  This is ridiculous." + '\n' +
        "Who does this?  Really?")
        return
    elif num > limits[unit]:
        await ctx.send(scold)
        return
    else:
        if unit[-1] != "s":
            unit += "s"
        delta = timedelta(**{unit: num})
        after_date = utcnow() - delta
        for channel in channels:
            handle = get(ctx.guild.channels, name=channel)
            if handle is None:
                await ctx.send(f"Channel {channel} not found.")
            else:
                try:
                    hist = await handle.history(after=after_date).flatten()
                except Forbidden:
                    await ctx.send(f"You do not have permission to get the history of {channel}")
                except HTTPException as e:
                    await ctx.send(f"There was an error getting {channel}.  The HTTP status code was {e.status}")
                else:
                    for message in hist:
                        await rename(message)
        await ctx.send("Completed.") 
 
@bot.command(hidden=True)
@commands.check(check_perms)
async def load(ctx, extension: str):
    await ctx.send("Attempting to load extension.")
    async def handle(cmd, *args):
        try:
            cmd(*args)
        except commands.ExtensionNotFound:
            await ctx.send(f"No such extension: {extension}.")
        except commands.ExtensionFailed as e:
            await ctx.send(f"Extension failed. {e.original.__class__.__name__}. {str(e.original)}")
        else:
            await ctx.send("Reloaded successfully.")
    try:
        await handle(bot.load_extension, extension)
    except commands.ExtensionAlreadyLoaded:
        await handle(bot.reload_extension,extension)

bot.load_extension("mtg")
bot.run(TOKEN)