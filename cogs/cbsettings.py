import discord
from discord import app_commands
from discord.ext import commands
from discord import Colour
from discord import ui
import json
import extensions.lists as lists
from extensions.uiactions import *
import core.ChatBot as ChatBot
from utils.jsonhandler import *
from utils.messagehandler import *

# commands that change a chatbot's settings
class ChatBotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("ChatBotSettings cog loaded.")
        
    # commands
    @app_commands.command(name="listchatbots", description="Lists all created chatbots")
    async def listchatbots(self, interaction: discord.Interaction) -> None:
        embed = discord.Embed(title="List of chatbots", colour=Colour.blue())
        for bot in lists.bot_instances[str(interaction.guild.id)]:
            embed.add_field(name=bot.name, value="", inline=False)
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="createchatbot", description="Creates a new chatbot. Use /enablehere (name) to enable the chatbot in the current channel")
    async def createchatbot(self, interaction:discord.Interaction) -> None:
        nc = CreateCBView()
        await interaction.response.send_modal(nc)
        
    @app_commands.command(name="settings", description="Change the settings for a specified chatbot\nType '/help settings' to learn about each setting.")
    async def settings(self, interaction:discord.Interaction) -> None:
        try:
            sett = SettingsView(interaction)
            await interaction.response.send_message(view=sett)  
        except Exception as e:
            print(e)
            
    @app_commands.command(name="chatbotinfo", description="Shows all settings for the specified chatbot")
    async def chatbotinfo(self, interaction:discord.Interaction, chatbot_name: str) -> None:
        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title="Error.", description="Bot does not exist. Please make sure you have entered the name correctly", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        try:
            channels = [self.bot.get_channel(channel_id).name for channel_id in cb.channels]
            out = f"""
            __**General**__
**Name:** {cb.name}
**Prompt:** {cb.prompt}
**Enabled:** {cb.enabled}
**Allowed Channels:** {", ".join(channels)}
**Prefixes:** {", ".join(cb.prefixes)}
**Include usernames:** {cb.include_usernames}

__**Output Generation**__
**Max Tokens:** {cb.max_tokens}
**Temperature:** {cb.temperature}
**Presence Penalty:** {cb.presence_penalty}
**Frequency Penalty:** {cb.frequency_penalty}
**Top P:** {cb.top_p}
**Max Message History Length:** {cb.max_message_history_length}
**Prompt Reminder Interval:** {cb.prompt_reminder_interval}
            """
            await send_msg(interaction, out)
        except Exception as e:
            print(e)
    
    @app_commands.command(name="showenabledhere", description="Shows all chatbots that are enabled in the current channel")
    async def showenabledhere(self, interaction:discord.Interaction) -> None:
        server = await get_server(interaction)
        embed = discord.Embed(title="List of chatbots enabled in current channel", description="\n".join([cb.name for cb in lists.bot_instances[str(interaction.guild.id)] if interaction.channel.id in cb.channels]), colour=Colour.blue())
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="enablehere", description = "Enables the specified chatbot in the current channel")
    async def enablehere(self, interaction:discord.Interaction, chatbot_name: str) -> None:
        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title="Error. Bot does not exist.", description="Please make sure you have entered the name correctly\nUse /listchatbots to see all created chatbots.", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        if interaction.channel.id not in cb.channels:  
                cb.channels.append(interaction.channel.id)
                await update_bot_json(interaction.guild.id, await make_bot_dict(cb))
                embed = discord.Embed(title=f"{cb.name} has been added to the current channel", colour=Colour.blue())
                await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"{cb.name} has already been added to the current channel", colour=Colour.blue())
            await interaction.response.send_message.send(embed=embed)
        
    @app_commands.command(name="disablehere", description="Disables the specified chatbot from the current channel.")
    async def disablehere(self, interaction: discord.Interaction, chatbot_name: str) -> None:
        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.channelremove Storywriter", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        cb.channels.remove(interaction.channel.id)
        await update_bot_json(interaction.guild.id, await make_bot_dict(cb))
        embed = discord.Embed(title=f"{cb.name} has been removed from the current channel", colour=Colour.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clearmessagehistory", description="Deletes the last given number of messages from the chatbot's memory. Leave num blank to clear all")
    async def clearmessagehistory(self, interaction: discord.Interaction, chatbot_name: str, num: int = -1) -> None:
        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.rmh Storywriter 4", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        try:
            ctxlen = len(cb.context)
            if num <= 0:
                cb.context.clear()
                embed = discord.Embed(title=f"Cleared message history for {cb.name}", description=f"{ctxlen} messages deleted", colour=Colour.blue())
                await interaction.response.send_message(embed=embed)
            else:   
                del cb.context[(-1 * num):]
                embed = discord.Embed(title=f"Cleared message history for {cb.name}", description=f"{min(ctxlen, num)} messages deleted", colour=Colour.blue())
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            ctxlen = len(cb.context)
            cb.context.clear()
            embed = discord.Embed(title=f"Cleared message history for {cb.name}", description=f"{ctxlen} messages deleted", colour=Colour.blue())
            await interaction.response.send_message(embed=embed)
            
    @app_commands.command(name="includeusernames", description = "Allows the specified chatbot to recognize usernames")
    async def includeusernames(self, interaction: discord.Interaction, chatbot_name: str, shouldiu: str) -> None:
        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.rmh Storywriter 4", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        shouldiu = shouldiu.lower()
        if shouldiu == 't' or shouldiu == "true" or shouldiu == "on":
            shouldiu = True
        elif shouldiu == 'f' or shouldiu == "false" or shouldiu == "off":
            shouldiu = False
        else:
            embed = discord.Embed(title=f"Error", description="Include usernames must be either true or false", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
            
        if cb.set_include_usernames(shouldiu):
            await update_bot_json(interaction.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Include usernames changed for {cb.name}", description=f"Include usernames is now:\n{str(shouldiu)}", colour=Colour.blue())
        else:
            embed = discord.Embed(title=f"Error", colour=Colour.red())
        await interaction.response.send_message(embed=embed)    
    
    @app_commands.command(name="deletechatbot", description = "Delete a chatbot")
    async def deletechatbot(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=DeleteChatView(interaction))

    
    @app_commands.command(name="removeprefix", description="Removes the selected prefixes from the specified chatbot\nSee '/help settings' for details on prefixes")
    async def removeprefix(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(view=RemovePrefixView)
        
    @app_commands.command(name="setdefault", description="Resets all settings for the specified chatbot to default")
    async def setdefault(self, interaction: discord.Interaction, chatbot_name: str) -> None:

        cb = await get_cb(interaction, chatbot_name)
        if not cb:
            embed = discord.Embed(title="Error", description="Please make sure you have entered the name correctly and try again.", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
            return
        newcb = ChatBot.ChatBot(name=cb.name)
        lists.bot_instances[str(interaction.guild.id)].remove(cb)
        lists.bot_instances[str(interaction.guild.id)].append(newcb)
        await update_bot_json(interaction.guild.id, await make_bot_dict(newcb))
        embed = discord.Embed(title=f"Successfully Reset Chatbot", description=f"All settings for {newcb.name} has been reset to default\n'/chatbotinfo {newcb.name}' to see its settings.", colour=Colour.blue())
        await interaction.response.send_message(embed=embed)
async def setup(bot):
    await bot.add_cog(ChatBotSettings(bot))