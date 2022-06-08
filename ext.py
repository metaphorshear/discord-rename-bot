from nextcord.ext import commands
from nextcord.utils import utcnow, get
from nextcord import Forbidden, HTTPException
from datetime import timedelta
from rename import rename

@commands.command()
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
                    async for message in handle.history(after=after_date):
                        await rename(message)
                except Forbidden:
                    await ctx.send(f"You do not have permission to get the history of {channel}")
                except HTTPException as e:
                    await ctx.send(f"There was an error getting {channel}.  The HTTP status code was {e.status}")
        await ctx.send("Completed.")
        
def setup(bot):
    bot.add_command(ago)