from operator import contains
from mtgsdk import Card
from common import *

class MTG(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        self.colors={"white": "#fcfdf0",
                "blue": "#0aa2c9",
                "black": "#19120f",
                "red": "#b9251d",
                "green": "#185234"}
        
    @commands.command()
    async def image(self, ctx, *name: str):
        cards = Card.where(name=" ".join(name)).where(contains='imageUrl').all()
        if len(cards) == 0:
            await ctx.send("No cards (with images) were found matching your query.")
            return
        embeds = []
        for card in cards:
            cembed = Embed(title=card.name,
                            color=self.colors[card.colors[0].lower()])
            cembed.set_image(card.imageUrl)
            embeds.append(cembed)
        await ctx.send(content=f"Here are your results, {ctx.author}.",
                       embeds=embeds)
        
            

        
def setup(bot):
    bot.add_cog(MTG(bot))