import discord
from discord.ext import commands
import json
import lists
import ChatBot
from jsonhandler import *
from discord import Colour

class ServerSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("ServerSettings cog loaded.")
        
    @commands.command()
    async def addadminrole(self, ctx) -> None:
        if not ctx.message.role_mentions:
            embed=discord.Embed(title="Error", description="Be sure to mention a role\nUsage: ai.setadminrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            return
        server_to_edit = await get_server(ctx)  
        if ctx.message.role_mentions[0].id not in server_to_edit.adminroles:
            server_to_edit.set_admin_roles(ctx.message.role_mentions[0])
            await update_server_json(ctx.guild.id, await make_settings_dict(server_to_edit))
            embed=discord.Embed(title="Added admin role", description=f"{ctx.message.role_mentions[0].mention} can now change chatbot settings.", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Error", description="Role already set as admin\nUsage: ai.setadminrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            
    @commands.command()
    async def removeadminrole(self, ctx) -> None:
        if not ctx.message.role_mentions:
            embed=discord.Embed(title="Error", description="Be sure to mention a role\nUsage: ai.setadminrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            return
        server_to_edit = await get_server(ctx)
        if ctx.message.role_mentions[0].id in server_to_edit.adminroles:
            server_to_edit.adminroles.remove(ctx.message.role_mentions[0].id)
            await update_server_json(ctx.guild.id, await make_settings_dict(server_to_edit))
            embed=discord.Embed(title="Removed admin role", description=f"{ctx.message.role_mentions[0].mention} is no longer a valid admin role.", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Error", description="Role is already not an admin role.\nUsage:\nai.removeadminrole @[role]", colour=Colour.red())
            await ctx.send(embed=embed)
            
            
    @commands.command()
    async def addallowedrole(self, ctx) -> None:
        if not ctx.message.role_mentions:
            embed=discord.Embed(title="Error", description="Be sure to mention a role\nUsage: ai.setadminrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            return
        server_to_edit = await get_server(ctx)  
        if ctx.message.role_mentions[0].id not in server_to_edit.allowedroles:
            server_to_edit.allowedroles.append(ctx.message.role_mentions[0].id)
            await update_server_json(ctx.guild.id, await make_settings_dict(server_to_edit))
            embed=discord.Embed(title="Allowed Role", description = f"Chatbot will now respond to users with {ctx.message.role_mentions[0].mention} role", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Error", description="Role already added\nUsage: ai.setallowedrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            
    @commands.command()
    async def removeallowedrole(self, ctx) -> None:
        if not ctx.message.role_mentions:
            embed=discord.Embed(title="Error", description="Be sure to mention a role\nUsage: ai.setadminrole @role", colour=Colour.red())
            await ctx.send(embed=embed)
            return
        server_to_edit = await get_server(ctx)
        if ctx.message.role_mentions[0].id in server_to_edit.allowedroles:
            server_to_edit.allowedroles.remove(ctx.message.role_mentions[0].id)
            await update_server_json(ctx.guild.id, await make_settings_dict(server_to_edit))
            embed=discord.Embed(title="Removed allowed role", description=f"Chatbot will no longer respond to users with {ctx.message.role_mentions[0].mention} role", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            embed=discord.Embed(title="Error", description="Role is already not an allowed role.\nUsage:\nai.removeadminrole @[role]", colour=Colour.red())
            await ctx.send(embed=embed)
            

async def setup(bot):
    await bot.add_cog(ServerSettings(bot))