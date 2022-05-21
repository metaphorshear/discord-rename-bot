import os
from nextcord.ext import commands
from dotenv import load_dotenv
import re
from time import time_ns

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
bot = commands.Bot(command_prefix='r!')
unknown = re.compile(r'unknown\.\w{2,4}$')
imagen = re.compile(r'image\d+\.\w{2,4}$')

@bot.listen('on_message')
async def rename(message):
    new_attachments = []
    for f in message.attachments:
        if re.search(unknown, f.filename) or re.search(imagen, f.filename):
                f.filename = f"{time_ns()}.{f.filename.split('.')[-1]}"
                fp = await f.to_file(use_cached=True)
                new_attachments.append(fp)
    if len(new_attachments) > 0:
        threads = message.channel.threads
        send_to = None
        for thread in threads:
            if thread.owner.bot:
                send_to = thread
        if send_to is None:
            send_to = await message.create_thread(name="renamed files", auto_archive_duration=60)
        await send_to.send(files=new_attachments)
                
                
bot.run(TOKEN)