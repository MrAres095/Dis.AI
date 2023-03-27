import discord
import asyncio
import os
import json
from discord.ext import commands
from discord import app_commands
import aiofiles
import interactions
import typing
import time

import core.ChatBot as ChatBot
import core.Server as Server
import utils.responses as responses
import config as config
import extensions.helpembeds as helpembeds
import extensions.lists as lists
import utils.jsonhandler as jsonhandler
import utils.messagehandler as messagehandler

# note to self: if adding new ChatBot properties, check make dict, checkjson, load, and ChatBot.py

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
background_tasks = set() # store api requests as tasks

bot = commands.Bot(command_prefix='ai.', intents=intents, application_id=config.APPLICATION_ID)
bot.remove_command('help')

@bot.command(name='sync')
async def sync(ctx):
    if ctx and not ctx.author.id == 215199288177721344:
        return
    try:
        fmt = await ctx.bot.tree.sync()
    except Exception as e:
        print(e)
    await ctx.send(f'Synced {len(fmt)} commands')

@bot.tree.command(name="help", description="Shows command list. Start here!") # ai.help command
async def help(interaction: discord.Interaction, page: str = "") -> None:
    if page.strip().lower() == "settings":
        await interaction.response.send_message(embed=helpembeds.help_embeds[1])
    elif page.strip().lower() == "2":
        await interaction.response.send_message(embed=helpembeds.help_embeds[2])
    else:
        await interaction.response.send_message(embed=helpembeds.help_embeds[0])

@bot.command()
async def checkjson(ctx=None):
    # Checking if the author of the command is the bot owner
    if ctx and not ctx.author.id == 215199288177721344:
        return
    # make sure that every server in the bot's serverlist has storage in the json. 
    # if not, create en entry and initialize it with a default bot (currently jarvis)
    data = {}
    needs_rewrite = False
    async with aiofiles.open('data.json', 'r') as f:
        json_data = await f.read()
        data = json.loads(json_data)

    for guild in bot.guilds:  # if the json doesn't contain the guild, add it.
        if str(guild.id) not in data:   
            needs_rewrite = True
            newbot = ChatBot.ChatBot(name="Jarvis")
            newserver = Server.Server(id=guild.id)
            def_bot = await jsonhandler.make_bot_dict(newbot)
            def_settings = await jsonhandler.make_settings_dict(newserver)
            data[guild.id] = {'server name': guild.name, 'settings': def_settings, 'bots': [def_bot]}
            
    if needs_rewrite:
        with open('data.json', 'w') as f:
            f.write(json.dumps(data, indent=4))
            
    # Load the data and send a message indicating that the json has been checked
    await load()
    if ctx:
        await ctx.send("[System]: Checked json.")
        
    


# functions below change a given ChatBot's properties
# starting here, and until otherwise noted, all functions modify the properties of a specified Chatot

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
    print("Online.")
    await checkjson(None)
    
@bot.event
async def on_guild_join(guild):
    await checkjson(None)
        
async def process_ai_response(current_server, message):
    for cb in lists.bot_instances[str(message.guild.id)]:   # for each chatbot in the server
        if (cb.enabled and message.channel.id in cb.channels): # if the given ChatBot is enabled and can talk in the channel
            
            if cb.include_usernames: # get username / nick if nicked
                if message.author.nick:
                    cb.context.append({'role':'user', 'content': f"{message.author.nick}: {str(message.content)}"})
                else:
                    cb.context.append({'role':'user', 'content': f"{message.author.name}: {str(message.content)}"})
            else: 
                cb.context.append({'role':'user', 'content': str(message.content)})
            
            #if allowedroles not set or author is guild owner or user has an allowed role, create completion task
            if not current_server.allowedroles or message.author.id == message.guild.owner.id or any(role in current_server.allowedroles for role in message.author.roles):
                if not cb.prefixes or any(message.content.startswith(prefix) for prefix in cb.prefixes):
                    async with message.channel.typing():
                        response = await responses.get_response(cb, message) # get response from openai
                        try:
                            if response[1] == -1:
                                embed = discord.Embed(title="Message failed OpenAI moderation check. Please comply with OpenAI usage policies.")
                                await response[0].channel.send(embed=embed)
                                continue
                            elif response[1] == -2:
                                try:
                                    embed = discord.Embed(title="Error: Message requested too many tokens.\n Please reduce max tokens (ai.mtk [chatbot name], recommended) or clear message history (ai.cmh [chatbot name] (num message to delete, leave empty to delete all))", color=discord.Colour.red())
                                    await response[0].channel.send(embed=embed)
                                    continue
                                except Exception as e:
                                    print("after mtk embed error")
                                    print(e)
                            await messagehandler.send_channel_msg(response[0].channel, str(response[1]['message']['content']))# max character count for messages is 2000. if the output is greater, split it into multiple messages
                            
                            print("Ran and sent task")
                        except Exception as e:
                            print(e )
                        

@bot.event
async def on_message(message):
    current_time = time.strftime("%H:%M:%S", time.localtime())
    
    try:
        current_server = await jsonhandler.get_server(message) # get Server that the message is from
        
        # process commands only if message author is admin, owner, or if no admins are set.
        if (message.content[0:3].lower() == 'ai.' or message.content[0] == '/') and (not current_server.adminroles or message.author.id == message.guild.owner.id or any(role in current_server.adminroles for role in message.author.roles)):
            await bot.process_commands(message)
            print(f"\n{current_time} {message.content}\n(server: '{message.guild.name}', channel: '{message.channel.name}')")
            return
        if message.author == bot.user: # don't process bot messages (may change later)
            return
        
        print(f"\n{current_time} {message.content}\n(server: '{message.guild.name}', channel: '{message.channel.name}')")
        await process_ai_response(current_server, message)
    except Exception as e:
        print(e)
    


async def load():
    # add all ChatBots to bot_instances
    lists.bot_instances.clear()
    lists.servers.clear()
    with open ('data.json', 'r') as f:
        servers_data = json.load(f)
        for server in servers_data:
            settings = servers_data[server]['settings']
            lists.servers.append(Server.Server(id=settings['id'], adminroles=settings['adminroles'], allowedroles=settings['allowedroles']))
            lists.bot_instances[server] = []
            for b in servers_data[server]['bots']:
                lists.bot_instances[server].append(ChatBot.ChatBot(name=b['name'], prompt=b['prompt'], max_tokens=b['max_tokens'],
                                             temperature=b['temperature'], top_p=b['top_p'], n=b['n'],
                                             presence_penalty=b['presence_penalty'],
                                             frequency_penalty=b['frequency_penalty'], enabled=b['enabled'],
                                             channels=b['channels'], server_id=int(server), 
                                             max_message_history_length=b['max_message_history_length'],
                                             prompt_reminder_interval=b['prompt_reminder_interval'], 
                                             include_usernames=b['include_usernames'], prefixes=b['prefixes']))
  
async def main():
    await load()
    TOKEN = config.DISCORD_TOKEN
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())