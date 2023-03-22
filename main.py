import discord
import asyncio
import os
import json
import ChatBot
from discord.ext import commands
import aiofiles
import responses
import lists
from jsonhandler import *
import Server
from helpembeds import help_embeds
from config import DISCORD_TOKEN
from messagehandler import *


# note to self: if adding new ChatBot properties, check make dict, checkjson, load, and ChatBot.py

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True
bot = commands.Bot(command_prefix='ai.', intents=intents, application_id='1080638505023193139')
background_tasks = set() # store api requests as tasks

bot.remove_command('help')
@bot.command() # ai.help command
async def help(ctx, *num) -> None:
    try:
        num = int(num[0])
    except:
        num = 1
    await ctx.send(embed=help_embeds[num - 1])

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
            def_bot = await make_bot_dict(newbot)
            def_settings = await make_settings_dict(newserver)
            data[guild.id] = {'server name': guild.name, 'settings': def_settings, 'bots': [def_bot]}
            
    if needs_rewrite:
        with open('data.json', 'w') as f:
            f.write(json.dumps(data, indent=4))
            
    # Load the data and send a message indicating that the json has been checked
    await load()
    if ctx:
        await ctx.send("[System]: Checked json.")
        
    
@bot.command(name='sync')
# currently useless
async def sync(self, ctx) -> None:
    fmt = await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send(f'Synced {len(fmt)} command(s)')

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
    game = discord.Game("ai.help to get started!")
    await bot.change_presence(status=discord.Status.online, activity=game)
    print("Online.")
    await checkjson(None)
    await run_bg_tasks()
    
@bot.event
async def on_guild_join(guild):
    await checkjson(None)
    
async def run_bg_tasks():
    # start the background task loop
    while True:
        if not background_tasks:
            # there are no tasks to run, so wait for a bit
            await asyncio.sleep(0)
            continue
        # get the first completed task from the set of background tasks
        print("Task detected. Running task")
        done, _ = await asyncio.wait(background_tasks, return_when=asyncio.FIRST_COMPLETED)
        print("Got completion:")
        # remove the completed task from the set of background tasks
        response = done.pop()
        background_tasks.remove(response)
        # process the API response, for example, send it as a message to the channel
        response = response.result()
        
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
        await send_msg(response[0].channel, str(response[1].message.content))# max character count for messages is 2000. if the output is greater, split it into multiple messages
        
        print("Ran and sent task")
            
@bot.event
async def on_message(message):
    server_to_edit = await get_server(message) # get Server that the message is from
    
    # process commands only if message author is admin, owner, or if no admins are set.
    if message.content[0:3].lower() == 'ai.' and (not server_to_edit.adminroles or message.author.id == message.guild.owner.id or any(role in server_to_edit.adminroles for role in message.author.roles)):
        await bot.process_commands(message)
        print(f"Processed command: {message.content}")
        return
    if message.author == bot.user: # don't process bot messages (may change later)
        return
    
    print(f"\nUser message received: '{message.content}'" )
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
            if not server_to_edit.allowedroles or message.author.id == message.guild.owner.id or any(role in server_to_edit.allowedroles for role in message.author.roles):
                if not cb.prefixes or any(message.content.startswith(prefix) for prefix in cb.prefixes):
                    background_tasks.add(asyncio.create_task(responses.get_response(cb, message))) # get response from openai
                    print("Added completion to tasks")


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
    TOKEN = DISCORD_TOKEN
    
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.start(TOKEN)

if __name__ == "__main__":
    asyncio.run(main())