import discord
from discord.ext import commands
from discord import app_commands
from discord import Colour
import json
import extensions.lists as lists
from extensions.uiactions import *
import core.ChatBot as ChatBot
import utils.jsonhandler as jsonhandler
class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("ServerSettings cog loaded.")
        
    @app_commands.command(name="addallowderole", description = "Adds allowed roles. If added, chatbots will only respond to a user of they have an allowed role.")
    async def addallowderole(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction)
            await interaction.response.send_message(view=ARView(interaction, server))
        except Exception as e:
            print(e)
            
    @app_commands.command(name="removeallowedrole", description="Removes allowed role")
    async def removeallowedrole(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction)
            if len(server.allowedroles) == 0:
                embed=discord.Embed(title="Error", description="No allowedroles have been set\nUse ```/addallowedroles``` to add roles\nIf no allowed roles have been set, then all users can interact with Dis.AI chatbots by default.", colour=Colour.red())
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(view=RARView(interaction, server))
        except Exception as e:
            print(e)
            
    @app_commands.command(name="addadminrole", description = "Add admin roles. If added, only admin roles can use commands. Otherwise, only the owner can.")
    async def addadminrole(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction)
            await interaction.response.send_message(view=AARView(interaction, server))
        except Exception as e:
            print(e)
            
    @app_commands.command(name="removeadminrole", description = "Removes admin role.")
    async def removeadminrole(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction)
            if len(server.adminroles) == 0:
                embed=discord.Embed(title="Error", description="No adminroles have been set\nUse ```/addallowedroles``` to add roles\nIf no allowed roles have been set, then all users can change the settings of Dis.AI chatbots by default.", colour=Colour.red())
                await interaction.response.send_message(embed=embed)
            else:
                await interaction.response.send_message(view=RAARView(interaction, server))
        except Exception as e:
            print(e)

            
            

            

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))