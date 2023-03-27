
import discord
from discord import app_commands
from discord.ext import commands
from discord import Colour
from discord import ui
import json
import extensions.lists as lists
import core.ChatBot as ChatBot
from utils.jsonhandler import *
from utils.messagehandler import *

class DeleteChatDropdown(ui.Select):
    def __init__(self, interaction):
        options =[discord.SelectOption(label=chatbot.name) for chatbot in lists.bot_instances[str(interaction.guild.id)]]
        super().__init__(placeholder="Select Chatbot(s) to Delete", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            self.disabled = True
            deletedbots = []
            for cbname in self.values:
                cb = await get_cb(interaction, cbname)
                if cb:
                    success = await delete_bot_json(interaction.guild.id, await make_bot_dict(cb))
                    if success:
                        lists.bot_instances[str(interaction.guild.id)].remove(cb)
                        deletedbots.append(cbname)
            outstr = '\n'.join(self.values)
            embed = discord.Embed(title=f"Deleted bot(s)", description=f"Deleted the following bots:\n{outstr}", colour=Colour.red())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)
        
class DeleteChatView(ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.add_item(DeleteChatDropdown(interaction))
        
class RemovePrefixDropdown(ui.Select):
    def __init__(self, interaction, cb):
        options =[discord.SelectOption(label=prefix) for prefix in cb.prefixes]
        super().__init__(placeholder="Select Prefix(es) to Delete", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        for prefix in self.values:
            cb.prefixes.remove(prefix)
        for cbname in self.values:
            cb = await get_cb(interaction, cb)
            await update_bot_json(interaction.guild.id, await make_bot_dict(cb))
        outstr = '\n'.join(self.values)
        embed = discord.Embed(title=f"Deleted bot(s)", description=f"Deleted the following bots: {outstr}", colour=Colour.red())
        await interaction.response.send_message(embed=embed)

class RemovePrefixView(ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.add_item(RemovePrefixDropdown(interaction))
        


class CreateCBView(ui.Modal, title="Enter New Chatbot Name"):
    name = ui.TextInput(label='Name')
    async def on_submit(self, interaction: discord.Interaction):

        try:
            for bot in lists.bot_instances[str(interaction.guild.id)]:
                if bot.name.strip().lower() == self.name.value.strip().lower():
                    embed = discord.Embed(title=f"New Chat Error", description=f"A chatbot with this name already exists. Please pick a different name.\nUse /listchatbots to show all created chatbots.", colour=Colour.red())
                    await interaction.response.send_message(embed=embed)
                    return
            newbot = ChatBot.ChatBot(name=self.name.value.strip(), server_id=interaction.guild.id, channels = [])
            await update_bot_json(interaction.guild.id, await make_bot_dict(newbot))
            lists.bot_instances[str(interaction.guild.id)].append(newbot)
            embed = discord.Embed(title=f"New chatbot created: {self.name}", description=f"```/enablehere {self.name}``` to enable the chatbot in the current channel\n```/settings``` to change settings (prompt, temperature, etc.)\n```/help``` for more commands", colour=Colour.blue())
            await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)

class ChatbotDropdown(ui.Select):
    def __init__(self, interaction):
        options =[discord.SelectOption(label=chatbot.name) for chatbot in lists.bot_instances[str(interaction.guild.id)]]
        super().__init__(placeholder="Select Chatbot to Configure", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.defer()
        cb = await get_cb(interaction, self.values[0])
        await interaction.followup.send(view=SettingsListView(cb))
        
class SettingsListDropdown(ui.Select):
    def __init__(self, cb):
        self.cb = cb
        options =[discord.SelectOption(label="Prompt"),
                  discord.SelectOption(label="Insert Message"),
                  discord.SelectOption(label="Temperature"),
                  discord.SelectOption(label="Presence Penalty"),
                  discord.SelectOption(label="Frequency Penalty"),
                  discord.SelectOption(label="Add Prefix"),
                  discord.SelectOption(label="Max Tokens"),
                  discord.SelectOption(label="Message History Length"),
                  discord.SelectOption(label="Prompt Reminder Interval"),
                  discord.SelectOption(label="Top P")
        ]
        super().__init__(placeholder="Select Setting ('/help settings' for details)", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        match self.values[0]:
            case "Prompt":
                await interaction.response.send_modal(PromptModal(self.cb))
            case "Insert Message":
                await interaction.response.send_modal(IMModal(self.cb))
            case "Temperature":
                await interaction.response.send_modal(TempModal(self.cb))
            case "Presence Penalty":
                await interaction.response.send_modal(PPModal(self.cb))
            case "Frequency Penalty":
                await interaction.response.send_modal(FPModal(self.cb))
            case "Add Prefix":
                await interaction.response.send_modal(APModal(self.cb))
            case "Max Tokens":
                await interaction.response.send_modal(MTKModal(self.cb))
            case "Message History Length":
                await interaction.response.send_modal(MHLModal(self.cb))
            case "Prompt Reminder Interval":
                await interaction.response.send_modal(PRIModal(self.cb))
            case "Top P":
                await interaction.response.send_modal(TopPModal(self.cb))
            case _:
                await interaction.response.send_message(f"Chose setting {self.values[0]}")

        
class SettingsView(ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.add_item(ChatbotDropdown(interaction))
      
class SettingsListView(ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.add_item(SettingsListDropdown(interaction))


class PromptModal(ui.Modal, title="Enter New Prompt"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    prompt = ui.TextInput(label="", style=discord.TextStyle.long, placeholder="Act as a snarky, witty, short-tempered AI named Jarvis. Only respond how Jarvis would.")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setPrompt(self.prompt.value):
            self.cb.context.clear()
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            try:
                embed = discord.Embed(title=f"Prompt changed for {self.cb.name}", description=self.cb.prompt, color=discord.Colour.blue())
                await interaction.response.send_message(embed=embed) 
            except Exception as e:
                print(e)
                await interaction.response.send_message(send_msg(interaction, f"Prompt changed for chatbot: {self.cb.name}\n{self.cb.prompt}")) 
        else:
            embed = discord.Embed(title="Error", description="Please try again", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
    
class IMModal(ui.Modal, title="Enter Message to Insert"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    role = ui.TextInput(label="Role", style=discord.TextStyle.short, placeholder="Possible roles: \"system\", \"assistant\", or \"user\"")
    content = ui.TextInput(label="Message", style=discord.TextStyle.long)
    async def on_submit(self, interaction: discord.Interaction):
        self.role = self.role.value.strip().lower()
        if self.role == "system" or self.role == "assistant" or self.role == "user":
            self.cb.context.append({'role':self.role,'content':self.content})
            embed = discord.Embed(title=f"Successfully Inserted Message", description=f"Inserted {self.role} message into chat history:\n{self.content}", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.temperature))
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title=f"Error", description="Enter a valid role\nPossible roles: \"system\", \"assistant\", or \"user\"", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed)
        
class TempModal(ui.Modal, title="Enter New Temperature"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    temp = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.9")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.settemp(self.temp.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Temperature changed for chatbot: {self.cb.name}", description="Temperature:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.temperature))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter a number between 0.0 and 2.0\n(Example: 0.9)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class PPModal(ui.Modal, title="Enter New Presence Penalty"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    pp = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.7")
    async def on_submit(self, interaction: discord.Interaction):
        try:
            if self.cb.setpp(self.pp.value):
                await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
                embed = discord.Embed(title=f"Presence Penalty changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
                embed.add_field(name="", value=str(self.cb.presence_penalty))
                await interaction.response.send_message(embed=embed) 
            else:
                embed = discord.Embed(title="Error", description="Enter a number between -2.0 and 2.0\n(Example: 0.7)", color=discord.Colour.red())
                await interaction.response.send_message(embed=embed) 
        except Exception as e:
            print(e)
            
class FPModal(ui.Modal, title="Enter New Frequency Penalty"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    fp = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.7")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setfp(self.fp.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Frequency Penalty changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.frequency_penalty))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter a number between -2.0 and 2.0\n(Example: 0.7)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class APModal(ui.Modal, title="Add New Prefix"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    prefix = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="hey ai")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.addprefix(self.prefix.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Added prefix for chatbot: {self.cb.name}", description=f"{self.cb.name} will now only respond if a message starts with one of the following prefixes:", color=discord.Colour.blue())
            embed.add_field(name="", value=", ".join(self.cb.prefixes))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Please try again.", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class MTKModal(ui.Modal, title="Enter New Max Token Amount"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="2048")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setmaxtk(self.response.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Max tokens changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.max_tokens))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter an integer between 0 and 4096\n(Example: 2048)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 

class MHLModal(ui.Modal, title="Enter New Max Message History Length"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="20")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.set_mmhl(self.response.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Max Message History Length changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.max_message_history_length))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter an integer greater than 0.\n(Example: 20)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class PRIModal(ui.Modal, title="Enter New Prompt Reminder Interval"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="10")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.set_pri(self.response.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Prompt Reminder Interval changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.prompt_reminder_interval))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter an integer greater than 0. \n(Example: 10)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class TopPModal(ui.Modal, title="Enter New Top P"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="1.0")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.settopp(self.response.value):
            await update_bot_json(interaction.guild.id, await make_bot_dict(self.cb))
            embed = discord.Embed(title=f"Top P for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.top_p))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter a number between 0.0 and 1.0\n(Example: 1.0)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
        
class ARDropdown(ui.RoleSelect):
    def __init__(self, interaction, server):
       #options = [discord.SelectOption(label=role.name) for role in interaction.guild.roles]
       self.server = server
       super().__init__(placeholder="Select Roles to Allow", min_values=1, max_values=25)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await self.server.set_allowed_roles([role.id for role in self.values])
            await update_server_json(interaction.guild.id, await make_settings_dict(self.server))
            out = "\n".join([role.name for role in self.values])
            embed = discord.Embed(title=f"Allowed roles", description=f"The following roles can now interact with Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed) 
        except Exception as e:
            print(e)

class ARView(ui.View):
    def __init__(self, interaction, server):
        super().__init__()
        self.add_item(ARDropdown(interaction, server))
        
class RARDropdown(ui.Select):
    def __init__(self, interaction, server):
       options = [discord.SelectOption(label=interaction.guild.get_role(roleid).name) for roleid in server.allowedroles]
       self.server = server
       super().__init__(placeholder="Select Allowed Roles to Disallow", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            AllowRoles = [interaction.guild.get_role(roleid) for roleid in self.server.allowedroles]
            for role in AllowRoles:
                if role.name in self.values:
                    self.server.allowedroles.remove(role.id)
            await update_server_json(interaction.guild.id, await make_settings_dict(self.server))
            out = "\n".join([rolename for rolename in self.values])
            embed = discord.Embed(title=f"Removed roles", description=f"The following roles can no longer interact with Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed) 
        except Exception as e:
            print(e)

class RARView(ui.View):
    def __init__(self, interaction, server):
        super().__init__()
        self.add_item(RARDropdown(interaction, server))
        
class AARView(ui.View):
    def __init__(self, interaction, server):
        super().__init__()
        self.add_item(AARDropdown(interaction, server))

class AARDropdown(ui.RoleSelect):
    def __init__(self, interaction, server):
       #options = [discord.SelectOption(label=role.name) for role in interaction.guild.roles]
       self.server = server
       super().__init__(placeholder="Select Roles to Select as Admin", min_values=1, max_values=25)
    
    async def callback(self, interaction: discord.Interaction):
        try:
            await self.server.set_admin_roles([role.id for role in self.values])
            await update_server_json(interaction.guild.id, await make_settings_dict(self.server))
            out = "\n".join([role.name for role in self.values])
            embed = discord.Embed(title=f"Admin roles", description=f"The following roles can now change the settings of Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed) 
        except Exception as e:
            print(e)

class RAARDropdown(ui.Select):
    def __init__(self, interaction, server):
       options = [discord.SelectOption(label=interaction.guild.get_role(roleid).name) for roleid in server.adminroles]
       self.server = server
       super().__init__(placeholder="Select Admin Role(s) to Remove", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        try:
            AdminRoles = [interaction.guild.get_role(roleid) for roleid in self.server.adminroles]
            print(AdminRoles)
            for role in AdminRoles:
                if role.name in self.values:
                    self.server.adminroles.remove(role.id)
            await update_server_json(interaction.guild.id, await make_settings_dict(self.server))
            out = "\n".join([rolename for rolename in self.values])
            embed = discord.Embed(title=f"Removed roles", description=f"The following roles can no longer change the settings of Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed) 
        except Exception as e:
            print(e)

class RAARView(ui.View):
    def __init__(self, interaction, server):
        super().__init__()
        self.add_item(RAARDropdown(interaction, server))