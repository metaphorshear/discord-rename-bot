from asyncio import Future
from nextcord.ext import commands
from nextcord.ui import View, button, Button
from io import BytesIO
from requests_futures.sessions import FuturesSession
from nextcord import Embed, ButtonStyle, Interaction
from typing import Any, Callable

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

class ResultsView(View):
    def __init__(self, content: list[Any], callback: Callable[[Any], Embed]):
        """View widget to paginate results.
        
        Parameters:
        content: a list of items.  the important thing is that the callback takes the same type of item.
        callback: a function to turn an item into an Embed.
        """
        super().__init__(timeout=None, auto_defer=False) 
        self.content = content
        self.page = 0
        self.callback = callback
        
    async def flip_page(self, interaction: Interaction, forward=True):
        if forward and self.page < len(self.content)-1:
            self.page += 1
        elif not forward and self.page > 0:
            self.page -= 1
        else:
            return
        hook = interaction.followup
        embed = await self.callback(self.content[self.page])
        #await hook.edit_message(interaction.message.id, embed=embed)
        await interaction.response.edit_message(embed=embed)
        
    
    @button(label="Prev <", style=ButtonStyle.grey)
    async def previous(self, button: Button, interaction: Interaction):
        await self.flip_page(interaction, forward=False)
            
            
    @button(label="Next >", style=ButtonStyle.green)
    async def next(self, button: Button, interaction: Interaction):
        await self.flip_page(interaction)

            
    @button(label="Done .", style=ButtonStyle.red)
    async def done(self, button: Button, interaction: Interaction):
        await interaction.response.edit_message(view=None)
        self.stop()
        
                                                    