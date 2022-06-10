from operator import contains
from mtgsdk import Card
from common import *

class MTG(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.colors={"white": 0xfcfdf0,
                "blue": 0x0aa2c9,
                "black": 0x19120f,
                "red": 0xb9251d,
                "green": 0x185234}
        
    @commands.command()
    async def cards(self, ctx, *name: str):
        name = " ".join(name)
        await ctx.send(f"Okay, searching for cards matching {name}")
        cards = Card.where(name=name).where(contains='imageUrl').all()
        if len(cards) == 0:
            await ctx.send("No cards (with images) were found matching your query.")
            return
        if len(cards) > 10:
            await ctx.send("Only the first 10 results will be shown.")
        cards = cards[:10]
        embeds = []
        for card in cards:
            color = Embed.Empty
            if card.colors is not None:
                color = self.colors[card.colors[0].lower()]
            cembed = Embed(title=card.name,
                            color=color)
            url = temp_url(card.image_url)
            if url is not None:
                cembed.set_image(url)
                embeds.append(cembed)
        if len(embeds) == 0 or all(True if e == Embed.Empty else False for e in embeds):
            await ctx.send(f"Sorry, {ctx.author}.  I have failed you.") 
        await ctx.send(content=f"Here are your results, {ctx.author}.",
                       embeds=embeds)
        
            

        
def setup(bot):
    bot.add_cog(MTG(bot))