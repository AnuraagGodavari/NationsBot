import discord
from discord.ext import commands

class CogTest(commands.Cog):
    def __init__(self, client):
        self.client = client
    
    #Cog Event
    @commands.Cog.listener()
    async def on_ready(self):
        print("Loaded CogTest.py")
    
    #Cog Command
    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(client.latency * 1000)}ms")
        
    @commands.command()
    async def displayembedCog(self, ctx): #Embeds can only have 24 lines
        newEmbed = discord.Embed(
            title = "Cog",
            description = "This is a description.",
            color = discord.Color.blue()
        )
        
        newEmbed.set_footer(text = "this is a footer")
        newEmbed.set_image(url = "https://media.discordapp.net/attachments/511327339272208385/703434717067870289/b6izq9dsew111.png?width=865&height=487")
        newEmbed.set_thumbnail(url = "https://media.discordapp.net/attachments/511327339272208385/741338602256203856/Indian_Soldier_Icon.png?width=394&height=400")
        newEmbed.set_author(name = "Author Name", icon_url = "https://media.discordapp.net/attachments/511327339272208385/741338602256203856/Indian_Soldier_Icon.png?width=394&height=400")
        
        for lineCounter in range(5):
            newEmbed.add_field(name = "Field Name", value = "Field Value", inline = False)
            
            for colCounter in range(10):
                newEmbed.add_field(name = "Field Name", value = "Field Value", inline = True)
        
        await ctx.send("Embed!", embed = newEmbed)
    
        
        
def setup(client):
    client.add_cog(CogTest(client))