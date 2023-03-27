import json
import extensions.lists as lists

async def get_cb(ctx, name):
    # get the chatbot to edit
    cb_to_edit = None
    if isinstance(name, str):
        for chatbot in lists.bot_instances[str(ctx.guild.id)]:
            if chatbot.name.lower() == name.strip().lower():
                cb_to_edit = chatbot
                break
    return cb_to_edit

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
        "prefixes":chatbot.prefixes
        }
    return dict

async def update_bot_json(server_id, bot):
    # updates the json file
    data = None
    server_id = str(server_id)
    with open('data.json', 'r') as f:
        data = json.load(f)
    b_list = data[server_id]['bots']
    for i in range(len(b_list)):
        if (b_list[i]['name'] == bot['name']):
            data[server_id]['bots'][i] = bot
            break 
    else:
        data[server_id]['bots'].append(bot)

    with open('data.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
        
async def delete_bot_json(server_id, bot):
    # deletes bot from json file
    data = None
    server_id = str(server_id)
    with open('data.json', 'r') as f:
        data = json.load(f)
    
    for chatbot in data[server_id]['bots']:
        if chatbot['name'] == bot['name']:
            data[server_id]['bots'].remove(bot)
            break
    else:
        return False
        

    with open('data.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
    return True
    
        
async def update_server_json(server_id, settings_dict):
    # updates the json file
    data = None
    server_id = str(server_id)
    with open('data.json', 'r') as f:
        data = json.load(f)
    data[server_id]['settings'] = settings_dict
    

    with open('data.json', 'w') as f:
        f.write(json.dumps(data, indent=4))
        
async def make_settings_dict(Server):   
    settings_dict = {
        'id':Server.id, 'adminroles':Server.adminroles, 'allowedroles': Server.allowedroles
        }
    return settings_dict