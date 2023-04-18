import discord
from discord.ext import commands
from discord import app_commands
from discord import Colour
from extensions.uiactions import *
from extensions.helpembeds import get_vote_embed
class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
        
    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("ServerSettings cog loaded.")
        
    @app_commands.command(name="addallowedrole", description = "Adds allowed roles. If added, chatbots will only respond to a user of they have an allowed role.")
    async def addallowedrole(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        await interaction.response.send_message(view=ARView(interaction, server))
            
    @app_commands.command(name="removeallowedrole", description="Removes allowed role")
    async def removeallowedrole(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        if len(server.allowedroles) == 0:
            embed=discord.Embed(title="Error", description="No allowedroles have been set\nUse ```/addallowedroles``` to add roles\nIf no allowed roles have been set, then all users can interact with Dis.AI chatbots by default.", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(view=RARView(interaction, server))
            
    @app_commands.command(name="addadminrole", description = "Add admin roles. If added, only admin roles can use commands. Otherwise, only the owner can.")
    async def addadminrole(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        await interaction.response.send_message(view=AARView(interaction, server))
            
    @app_commands.command(name="removeadminrole", description = "Removes admin role.")
    async def removeadminrole(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        if len(server.adminroles) == 0:
            embed=discord.Embed(title="Error", description="No adminroles have been set\nUse ```/addallowedroles``` to add roles\nIf no allowed roles have been set, then all users can change the settings of Dis.AI chatbots by default.", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(view=RAARView(interaction, server))
            
    @app_commands.command(name="setkey", description = "Set your OpenAI API key.")
    async def setkey(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        await interaction.response.send_modal(OpenAIKeyModal(server))
        
    @app_commands.command(name="removekey", description = "Remove your OpenAI API key.")
    async def removekey(self, interaction: discord.Interaction) -> None:
        server = await get_server(interaction.guild.id)
        server.openai_key = ""
        await change_server_setting_in_db(server.id, "openai_key", str(server.openai_key))
        embed=discord.Embed(title="Removed API key", color=Colour.blue())
        await interaction.response.send_message(embed=embed)      
    @app_commands.command(name="vote", description = "Vote for Dis.AI to reset today's message limit!")
    async def vote(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction.guild.id)
            server.voting_channel_id = interaction.channel.id
            embed = await get_vote_embed(interaction.guild.id)
            await interaction.response.send_message(embed=embed)      
        except Exception as e:
            print(e)
            
    @app_commands.command(name="messagecount", description = "See how many messages this server has sent today.")
    async def messagecount(self, interaction: discord.Interaction) -> None:
        try:
            server = await get_server(interaction.guild.id)
            embed=discord.Embed(title=f"Message Count for {interaction.guild.name}", description=f"`{server.dailymsgs} / 25`\n\nWant to reset your message count to 0? Use `/vote`!", color=Colour.blue())
            await interaction.response.send_message(embed=embed)      
        except Exception as e:
            print(e)
            
    
            

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))