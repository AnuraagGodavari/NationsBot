import discord
import os
from discord.ext import commands

client = commands.Bot(command_prefix = "n.")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game("Concert of Nations"))
    print("NationsBot is ready!")

#Loads a cog
@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")

#Loads a cog
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")

#Go through all the files in the "cogs" folder in this directory, load them all.
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        #If filename is "example.py", filename[:-3] returns "example"
        client.load_extension(f"cogs.{filename[:-3]}")
        
#Loads the GameCogs file for running Games.
client.load_extension(f"ConcertOfNationsCogs.GameCogs")
    
    
client.run("NTQ5MjY0MTgyNDA3NzI1MDk4.XHLEIQ.Gi-VksnAE6QYgJ66qqD62EsqAiU")