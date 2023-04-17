import discord
import asyncio
import aiofiles
import os
import json
from discord.ext import commands
from datetime import datetime, time, timezone
from EdgeGPT import Chatbot
import utils.responses as responses
from config import DISCORD_TOKEN, APPLICATION_ID, DBL_TOKEN
import extensions.helpembeds as helpembeds
from extensions.lists import bot_instances, servers
from utils import jsonhandler, messagehandler
import pytz
import topgg
from discord.ext import tasks
eastern = pytz.timezone('US/Eastern')

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


reset_time = time(hour=7, minute=30, tzinfo=timezone.utc)

bot = commands.Bot(command_prefix='ai.', intents=intents, application_id=APPLICATION_ID)
bot.remove_command('help')

@tasks.loop(time=reset_time)
async def reset_daily_msgs():
    try:
        for server in servers:
            server.dailymsgs = 0
        print(f"Reset all dailymsgs")
    except Exception as e:
        print(f"Failed to reset msgs")



async def setup_topgg():
    bot.topggpy = topgg.DBLClient(bot, DBL_TOKEN)
    bot.topgg_webhook = topgg.WebhookManager(bot).dbl_webhook("/dblwebhook", "agentwebweb123123")
    bot.topgg_webhook.run(5000)  # this method can be awaited as well
    print("setup topgg")
    
    
@bot.event
async def on_dbl_vote(data):
    """An event that is called whenever someone votes for the bot on Top.gg."""
    print("someone voted")
    print(data)
    if data["type"] == "test":
        # this is roughly equivalent to
        # `return await on_dbl_test(data)` in this case
        return bot.dispatch("dbl_test", data)

    print(f"Received a vote:\n{data}")


@bot.event
async def on_dbl_test(data):
    print("1")
    """An event that is called whenever someone tests the webhook system for your bot on Top.gg."""
    print(f"Received a test vote:\n{data}")

 

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
    elif page.strip().lower() == "3":
        await interaction.response.send_message(embed=helpembeds.help_embeds[3])
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
    try:
        for server in bot_instances:
            await jsonhandler.change_server_setting_in_db(server.id, "adminroles", server.adminroles)
            await jsonhandler.change_server_setting_in_db(server.id, "allowedroles", server.allowedroles)
            await jsonhandler.change_server_setting_in_db(server.id, "dailymsgs", server.dailymsgs)
            await jsonhandler.change_server_setting_in_db(server.id, "openai_key", server.openai_key)
            for chatbot in bot_instances[server]:
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "name", chatbot.context)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "prompt", chatbot.prompt)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "max_tokens", chatbot.max_tokens)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "temperature", chatbot.temperature)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "top_p", chatbot.top_p)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "n", chatbot.n)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "presence_penalty", chatbot.presence_penalty)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "frequency_penalty", chatbot.frequency_penalty)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "enabled", chatbot.enabled)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "channels", chatbot.channels)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "server_id", chatbot.server_id)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "max_message_history_length", chatbot.max_message_history_length)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "prompt_reminder_interval", chatbot.prompt_reminder_interval)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "include_usernames", chatbot.include_usernames)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "prefixes", chatbot.prefixes)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "search_prefixes", chatbot.search_prefixes)
                await jsonhandler.change_cb_setting_in_db(server, chatbot.name, "context", chatbot.context)
        await bot.close()
        raise SystemExit(0)
    except Exception as e:
        print(e)

        
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
    try:
        game = discord.Game("/createchatbot")
        await bot.change_presence(status=discord.Status.online, activity=game)
        await setup_topgg()
        await jsonhandler.checkdb(bot)
        
        
        print("finished checkdb")
        await jsonhandler.load_db_to_mem(bot.guilds)
        print("finished load mem")
        # await reset_msgs()
        reset_daily_msgs.start()
        print("done on ready")
    except Exception as e:
        print("on ready err")
        print(e)
    
@bot.event
async def on_guild_join(guild):
    print(f"New guild joined: {guild.name}")
    await jsonhandler.add_guild_to_db(guild)

@bot.event
async def on_message(message):
    if message.author == bot.user: # don't process bot messages (may change later)
        return
    now = datetime.now()
    formatted_date = now.strftime("%m/%d %H:%M:%S")

    current_server = await jsonhandler.get_server(message.guild.id) # get Server that the message is from
    print(f"\n{formatted_date} {message.author.name}: {message.content}\n(server: '{message.guild.name}', channel: '{message.channel.name}')")
    # process commands only if message author is admin, owner, or if no admins are set.
    if (not current_server.adminroles or message.author.id == message.guild.owner.id or any(role in current_server.adminroles for role in message.author.roles)):
        if message.content.startswith("ai."):
            print("processing ai. command")
            await bot.process_commands(message)
            return
    try:
        await messagehandler.process_ai_response(current_server, message)
    except Exception as e:
        print(e)


async def main():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
            
    await bot.start(DISCORD_TOKEN)

if __name__ == "__main__":
    asyncio.run(main())