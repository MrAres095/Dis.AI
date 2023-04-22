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
from extensions.helpembeds import help_embeds, discordEmbed
from extensions.lists import bot_instances, servers
from utils import jsonhandler, messagehandler
import pytz
import topgg
from discord.ext import tasks
from encryption import encrypt
eastern = pytz.timezone('US/Eastern')

# intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.guilds = True


reset_time = time(hour=16, minute=00, tzinfo=timezone.utc)

bot = commands.Bot(command_prefix='ai.', intents=intents, application_id=APPLICATION_ID)
bot.remove_command('help')

@tasks.loop(minutes=30)
async def update_stats():
    try:
        if bot.user.id != 1087577022693384263:
            await bot.topggpy.post_guild_count()
            print(f"Posted server count ({bot.topggpy.guild_count})")
        else:
            print("In test, not posting")
    except Exception as e:
        print(f"Failed to post server count\n{e.__class__.__name__}: {e}")


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
    channel=interaction.channel
    if page.strip().lower() == "settings":
        await interaction.response.send_message(embed=help_embeds[1])
        await channel.send(embed=discordEmbed)
        await channel.send("https://discord.gg/xsXD7AafX5")
    elif page.strip().lower() == "2":
        await interaction.response.send_message(embed=help_embeds[2])
        await channel.send(embed=discordEmbed)
        await channel.send("https://discord.gg/xsXD7AafX5")
    elif page.strip().lower() == "3":
        await interaction.response.send_message(embed=help_embeds[3])
        await channel.send(embed=discordEmbed)
        await channel.send("https://discord.gg/xsXD7AafX5")
    else:
        await interaction.response.send_message(embed=help_embeds[0])
        await channel.send(embed=discordEmbed)
        await channel.send("https://discord.gg/xsXD7AafX5")
        

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
    key = encrypt.generate_key()
    try:
        for server in servers:
            try:
                guild = await bot.fetch_guild(server.id)
                def_settings = await jsonhandler.set_server(guild, server)
            except Exception as e:
                print(e)
            
        raise SystemExit(0)
    except Exception as e:
        print("shutdown error")
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
        print(encrypt.get_key())
        await jsonhandler.checkdb(bot)
        
        
        print("finished checkdb")
        await jsonhandler.load_db_to_mem(bot.guilds)
        print("finished load mem")
        reset_daily_msgs.start()
        update_stats.start()
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
    if message.channel.id == 1097027491375370242:
        print("User voted")
        fet = str(message.content)
        try:
            guildid = int(fet[fet.index('a') + 2:fet.index(' ')])
            user = int(fet[fet.index("user") + 5:fet.index(" ", fet.index("user") + 5)])
            server = await jsonhandler.get_server(guildid)
            guild = await bot.fetch_guild(guildid)
            channel = await guild.fetch_channel(server.voting_channel_id)
            server.dailymsgs = 0
            embed=discord.Embed(title="Thank you for voting for Dis.AI!", description=f"<@{user}> has voted for Dis.AI!\nThis server's message limit has been reset to 0!```You can vote again in 12 hours!```", color=discord.Colour.blue())
            embed.set_thumbnail(url='https://github.com/jacobjude/Dis.AI/blob/master/icon.png?raw=true')
            await channel.send(embed=embed)
            print("Successfully reset dailymsgs")
        except Exception as e:
            print(e)
        return
    elif message.channel.id == 1098342622373883924:
        print("User posted in daily limit channel")
        try:
            guildid = int(message.content)
            server = await jsonhandler.get_server(guildid)
            
        except Exception as e:
            print(e)
            await message.channel.send(f"<@{message.author.id}> Invalid server id. See pins for information on how to get your server id.\nBe sure to paste ONLY the server id. ")
            return
            
        server.dailymsgs = 0
        await message.channel.send(f"<@{message.author.id}> Successfully reset the message count for your server to zero.")
            
        
    now = datetime.now()
    formatted_date = now.strftime("%m/%d %H:%M:%S")
    
    

    current_server = await jsonhandler.get_server(message.guild.id) # get Server that the message is from
    print(f"\n{formatted_date} {message.author.name} \n(server: '{message.guild.name}', channel: '{message.channel.name}'), key: {bool(current_server.openai_key)}")
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