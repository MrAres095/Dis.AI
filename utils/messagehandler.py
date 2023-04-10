import discord
from utils import responses
import extensions.lists as lists
import asyncio


async def process_ai_response(current_server, message):
    for cb in lists.bot_instances[message.guild.id]:   # for each chatbot in the server
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
                should_search = False
                if cb.search_prefixes and any(message.content.startswith(search_prefix) for search_prefix in cb.search_prefixes):
                    should_search = True
                if (should_search or not cb.prefixes or any(message.content.startswith(prefix) for prefix in cb.prefixes)):
                    async with message.channel.typing():
                        if message.content: # moderate user message
                            errors = await responses.get_moderation(message.content) 
                            errors = False
                            if errors:
                                del cb.context[-1]
                                embed = discord.Embed(title="Message failed OpenAI moderation check. Please comply with OpenAI usage policies.", color = discord.Colour.red())
                                await message.channel.send(embed=embed)
                                return
                        if should_search:
                            search_prefix = [prefix for prefix in cb.search_prefixes if message.content.startswith(prefix)][0]
                            print("getting bing response")
                            bing_response = await responses.get_bing_response(message.content.replace(search_prefix, "", 1).lstrip(), cb.bing_bots[message.channel.id])
                            cb.context.append({'role': 'system', 'content': f"A web search yielded the following result. With this new information, answer the user's question according to your original prompt and previous conversation messages.\n\"{bing_response}\""})
                            print("got bing response and appended")
                        print("getting response")
                        response = await responses.get_response(cb, message) # get response from openai
                        print("got response")
                        if response[0] == -1:
                            embed = discord.Embed(title="Message failed OpenAI moderation check. Please comply with OpenAI usage policies.", color = discord.Colour.red())
                            await message.channel.send(embed=embed)
                        elif response[0] == -2:
                            if len(response[1]) > 1:
                                embed = discord.Embed(title="An error occurred.", description=f"Error: Too many tokens requested. Please use ```/clearmessagehistory``` or reduce max tokens in ```/settings```", color=discord.Colour.red())
                            else:
                                embed = discord.Embed(title="An error occurred. Please try again.", description="Error: Response took too long.", color=discord.Colour.red())
                            await message.channel.send(embed=embed)
                        else:
                            await send_channel_msg(message.channel, str(response[1]['message']['content']))# max character count for messages is 2000. if the output is greater, split it into multiple messages
                            print(response[1]['message'])

async def send_msg(interaction, msg):
    max_msgs = (len(msg) // 2000) + 1
    if max_msgs > 1:
        for i in range(max_msgs):
            await interaction.response.send_message(msg[i*1990:(i+1)*1990] + f" ({i + 1}/{max_msgs})")
    else:
        await interaction.response.send_message(str(msg))
        
async def send_channel_msg(channel, msg):
    max_msgs = (len(msg) // 2000) + 1
    if max_msgs > 1:
        for i in range(max_msgs):
            await channel.send(msg[i*1990:(i+1)*1990] + f" ({i + 1}/{max_msgs})")
    else:
        await channel.send(str(msg))
        
async def force_ai_response(interaction, chatbot, numTimes = 1):
    
    embed=discord.Embed(title="Forcing responses", color=discord.Colour.blue())
    await interaction.response.send_message(embed=embed)
    try:
        for i in range(numTimes):
            response = await responses.get_response(chatbot, None) # get response from openai
            await send_channel_msg(interaction.channel, str(response[1]['message']['content']))
    except Exception as e:
        print("far")
        print(e)