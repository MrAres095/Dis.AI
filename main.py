import discord
import asyncio
import aiofiles
import os
import json
from discord.ext import commands
import time
from EdgeGPT import Chatbot
import utils.responses as responses
from config import DISCORD_TOKEN, APPLICATION_ID
import extensions.helpembeds as helpembeds
from extensions.lists import bot_instances, servers
from utils import jsonhandler, messagehandler

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
background_tasks = set() # store api requests as tasks

bot = commands.Bot(command_prefix='ai.', intents=intents, application_id=APPLICATION_ID)
bot.remove_command('help')

@bot.command(name='sync')
async def sync(ctx):
    if ctx and not ctx.author.id == 215199288177721344:
        return
    fmt = await ctx.bot.tree.sync()
    await ctx.send(f'Synced {len(fmt)} commands')

@bot.tree.command(name="help", description="Shows command list. Start here!") # ai.help command
async def help(interaction: discord.Interaction, page: str = "") -> None:
    if page.strip().lower() == "settings":
        await interaction.response.send_message(embed=helpembeds.help_embeds[1])
    elif page.strip().lower() == "2":
        await interaction.response.send_message(embed=helpembeds.help_embeds[2])
    else:
        await interaction.response.send_message(embed=helpembeds.help_embeds[0])

@bot.command(name='initdb')
async def initdb(ctx):
    if ctx and not ctx.author.id == 215199288177721344:
        return
    await jsonhandler.load_db_to_mem(bot.guilds)
    await ctx.send("[System]: Initialized db with current servers and default bots.")
        
        
@bot.command()
@commands.is_owner()
async def shutdown(ctx):
    if ctx and not ctx.author.id == 215199288177721344:
        return
    print("shutdown")
    await responses.shutbot()
    await bot.close()
    raise SystemExit(0)

        
# load and unload
@bot.command()
async def reload(ctx):
    try:
        if not ctx.author.id == 215199288177721344:
            return
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await bot.unload_extension(f'cogs.{filename[:-3]}')
                await bot.load_extension(f'cogs.{filename[:-3]}')
        await ctx.send("Cogs reloaded")
    except Exception as e:
        print(e)
        await ctx.send("Reload error")

@bot.event
async def on_ready():
    game = discord.Game("/createchatbot")
    await bot.change_presence(status=discord.Status.online, activity=game)
    await jsonhandler.checkdb(bot)
    await jsonhandler.load_db_to_mem(bot.guilds)
    
@bot.event
async def on_guild_join(guild):
    print(f"New guild joined: {guild.name}")
    await jsonhandler.add_guild_to_db(guild)

@bot.event
async def on_message(message):
    if message.author == bot.user: # don't process bot messages (may change later)
        return
    current_time = time.strftime("%H:%M:%S", time.localtime())
    current_server = await jsonhandler.get_server(message) # get Server that the message is from
    print(f"\n{current_time} {message.author.name}: {message.content}\n(server: '{message.guild.name}', channel: '{message.channel.name}')")
    # process commands only if message author is admin, owner, or if no admins are set.
    if (not current_server.adminroles or message.author.id == message.guild.owner.id or any(role in current_server.adminroles for role in message.author.roles)):
        if message.content.startswith("ai."):
            print("processing ai. command")
            await bot.process_commands(message)
            return
    
    await messagehandler.process_ai_response(current_server, message)


async def main():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())