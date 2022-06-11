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
        self.cache = {}
        
    async def card_embed(self, card: 'Card'):
        color = Embed.Empty
        if card.colors is not None:
            color = self.colors[card.colors[0].lower()]
        cembed = Embed(title=f"{card.name} ({card.number})",
                        color=color)
        if card in self.cache:
            url = self.cache[card]
        else:
            url = temp_url(card.image_url)
        if url is not None:
            self.cache[card] = url
            cembed.set_image(url)   
            return cembed
    
    @commands.command()
    async def cards(self, ctx, *name: str):
        name = " ".join(name)
        await ctx.send(f"Okay, searching for cards matching \"{name}\"")
        cards = Card.where(name=name).where(contains='imageUrl').all()
        if len(cards) == 0:
            await ctx.send("No cards (with images) were found matching your query.")

        view = ResultsView(cards, self.card_embed)
        embed= await self.card_embed(cards[0])
        await ctx.send(content=f"Here are your results, {ctx.author}.",
                       embed=embed,
                       view=view)
        
            

        
def setup(bot):
    bot.add_cog(MTG(bot))