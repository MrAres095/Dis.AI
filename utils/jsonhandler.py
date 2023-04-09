import pymongo
import json
import extensions.lists as lists
from config import MONGO_LINK, COOKIES
import core.ChatBot as ChatBot
import core.Server as Server
from EdgeGPT import Chatbot

mongoclient = pymongo.MongoClient(MONGO_LINK)
db = mongoclient["DisAI"]
print("created mongo client")

async def checkdb(bot):
    for guild in bot.guilds:
        await add_guild_to_db(guild)

async def add_guild_to_db(guild):
    if not [gid for gid in db.servers.find({"_id": guild.id})]:
            newbot = ChatBot.ChatBot(name="Jarvis")
            newserver = Server.Server(id=guild.id)
            lists.servers.append(newserver)
            lists.bot_instances[guild.id] = [newbot]
            def_bot = await make_bot_dict(newbot)
            def_settings = await make_settings_dict(newserver)
            db.servers.insert_one({
                "_id": guild.id,
                "server_name": guild.name,
                "settings": def_settings,
                "bots": [def_bot]
                })

async def load_db_to_mem(guilds):
    # add all ChatBots to lists.bot_instances and servers to lists.servers
    lists.servers.clear()
    lists.bot_instances.clear()
    for server in db.servers.find():
        if server['_id'] not in [server.id for server in lists.servers]:
            lists.servers.append(Server.Server(id=server['_id'], adminroles=server['settings']['adminroles'], allowedroles=server['settings']['allowedroles']))
            lists.bot_instances[server['_id']] = []

        for b in server['bots']:
            if b['name'] not in [bot.name for bot in lists.bot_instances[server['_id']]]:
                nb = ChatBot.ChatBot(name=b['name'], prompt=b['prompt'], max_tokens=b['max_tokens'],
                                            temperature=b['temperature'], top_p=b['top_p'], n=b['n'],
                                            presence_penalty=b['presence_penalty'],
                                            frequency_penalty=b['frequency_penalty'], enabled=b['enabled'],
                                            channels=b['channels'], server_id=server['_id'], 
                                            max_message_history_length=b['max_message_history_length'],
                                            prompt_reminder_interval=b['prompt_reminder_interval'], 
                                            include_usernames=b['include_usernames'], prefixes=b['prefixes'], search_prefixes=b['search_prefixes'], context=b['context'])
                lists.bot_instances[server['_id']].append(nb)
                
                for channelid in lists.bot_instances[server['_id']][-1].channels:
                    try:
                        lists.bot_instances[server['_id']][-1].bing_bots[channelid] = Chatbot(cookies=COOKIES)
                    except Exception as e:
                        print("bingbot failed")
                
async def add_cb_to_db(guildid, dict):
    db.servers.update_one({"_id": guildid}, {"$push": {"bots": dict}})

async def remove_cb_from_db(guildid, botname):
    db.servers.update_one({"_id": guildid}, {"$pull": {"bots": {"name": botname}}})
    
async def change_cb_setting_in_db(guildid, botname, setting, newvalue):
        db.servers.update_one({"_id": guildid, "bots": { "$elemMatch": { "name": botname } }}, {"$set": { f"bots.$.{setting}": newvalue } })
    
async def change_server_setting_in_db(guildid, setting, newvalue):
    db.servers.update_one({"_id": guildid}, {"$set": { f"settings.{setting}": newvalue } })
    
async def get_cb(ctx, name):
    # get the chatbot to edit
    cb_to_edit = None
    if isinstance(name, str):
        for chatbot in lists.bot_instances[ctx.guild.id]:
            if chatbot.name.lower() == name.strip().lower():
                return chatbot
    return None

async def get_server(ctx):
    server_to_edit = None
    for server in lists.servers:
        if ctx.guild.id == server.id:
            server_to_edit = server
            break
    
    return server_to_edit

async def make_bot_dict(chatbot):
    # given a ChatBot, format it into a dictionary for export
    dict = {
        'name': chatbot.name,
        "prompt": chatbot.prompt,
        "max_tokens": chatbot.max_tokens,
        "temperature": chatbot.temperature,
        "top_p": chatbot.top_p,
        "n": chatbot.n,
        "presence_penalty": chatbot.presence_penalty,
        "frequency_penalty": chatbot.frequency_penalty,
        "enabled": chatbot.enabled,
        "channels": chatbot.channels,
        "server_id": chatbot.server_id,
        "max_message_history_length": chatbot.max_message_history_length,
        "prompt_reminder_interval":chatbot.prompt_reminder_interval,
        "include_usernames": chatbot.include_usernames,
        "prefixes":chatbot.prefixes,
        "search_prefixes":chatbot.search_prefixes,
        "context": chatbot.context
        }
    return dict
        
async def make_settings_dict(Server):   
    settings_dict = {
        'adminroles':Server.adminroles, 'allowedroles': Server.allowedroles
        }
    return settings_dict