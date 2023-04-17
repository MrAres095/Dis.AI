
import discord
from discord.ext import commands
from discord import Colour
from discord import ui
import extensions.lists as lists
import core.ChatBot as ChatBot
from utils.jsonhandler import *

class DeleteChatDropdown(ui.Select):
    def __init__(self, interaction):
        options =[discord.SelectOption(label=chatbot.name) for chatbot in lists.bot_instances[interaction.guild.id]]
        super().__init__(placeholder="Select Chatbot(s) to Delete", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        for cbname in self.values:
            lists.bot_instances[interaction.guild.id].remove(await get_cb(interaction, cbname))
            await remove_cb_from_db(interaction.guild.id, cbname)
        outstr = '\n'.join(self.values)
        embed = discord.Embed(title=f"Deleted bot(s)", description=f"Deleted the following bots:\n{outstr}", colour=Colour.red())
        await interaction.response.send_message(embed=embed)
        
class DeleteChatView(ui.View):
    def __init__(self, interaction):
        super().__init__()
        self.add_item(DeleteChatDropdown(interaction))
        
class RemovePrefixDropdown(ui.Select):
    def __init__(self, cb):
        self.cb = cb
        options =[discord.SelectOption(label=prefix) for prefix in cb.prefixes]
        super().__init__(placeholder="Select Prefixes to Delete", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        for prefix in self.values:
            self.cb.prefixes.remove(prefix)
        
        # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "prefixes", self.cb.prefixes)
        outstr = '\n'.join(self.values)
        embed = discord.Embed(title=f"Deleted prefixes", description=f"Deleted the following prefixes:\n{outstr}", colour=Colour.blue())
        await interaction.response.send_message(embed=embed)

class RemovePrefixView(ui.View):
    def __init__(self, cb):
        super().__init__()
        
        self.add_item(RemovePrefixDropdown(cb))

class CreateCBView(ui.Modal, title="Enter New Chatbot Name"):
    name = ui.TextInput(label='Name')
    async def on_submit(self, interaction: discord.Interaction):
        for bot in lists.bot_instances[interaction.guild.id]:
            if bot.name.strip().lower() == self.name.value.strip().lower():
                embed = discord.Embed(title=f"New Chat Error", description=f"A chatbot with this name already exists. Please pick a different name.\nUse /listchatbots to show all created chatbots.", colour=Colour.red())
                await interaction.response.send_message(embed=embed)
                return
        newbot = ChatBot.ChatBot()
        newbot.name = self.name.value.strip()
        newbot.server_id=interaction.guild.id
        newbot.context.clear()
        newbot.prefixes.clear()
        newbot.search_prefixes=["search"]
        newbot.channels.clear()
        print(f"{newbot.name} {newbot.server_id} {newbot.channels} {newbot.prompt} {newbot.context}")
        await add_cb_to_db(interaction.guild.id, await make_bot_dict(newbot))
        lists.bot_instances[interaction.guild.id].append(newbot)
        embed = discord.Embed(title=f"New chatbot created: {self.name}", description=f"```/enablehere {self.name}``` to enable the chatbot in the current channel\n```/settings``` to change settings (prompt, temperature, etc.)\n```/help``` for more commands", colour=Colour.blue())
        await interaction.response.send_message(embed=embed)

class ChatbotDropdown(ui.Select):
    def __init__(self, interaction):
        options =[discord.SelectOption(label=chatbot.name) for chatbot in lists.bot_instances[interaction.guild.id]]
        super().__init__(placeholder="Select Chatbot to Configure", options=options, min_values=1, max_values=1)
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        await interaction.response.defer()
        cb = await get_cb(interaction, str(self.values[0]))
        await interaction.followup.send(view=SettingsListView(cb))
        
class SettingsListDropdown(ui.Select):
    def __init__(self, cb):
        self.cb = cb
        options =[discord.SelectOption(label="Prompt"),
                  discord.SelectOption(label="Insert Message"),
                  discord.SelectOption(label="Message History Length"),
                  discord.SelectOption(label="Prompt Reminder Interval"),
                  discord.SelectOption(label="Include Usernames"),
                  discord.SelectOption(label="Add Prefix"),
                  discord.SelectOption(label="Remove Prefix"),
                  discord.SelectOption(label="Add Search Prefix"),
                  discord.SelectOption(label="Remove Search Prefix"),
                  discord.SelectOption(label="Temperature"),
                  discord.SelectOption(label="Presence Penalty"),
                  discord.SelectOption(label="Frequency Penalty"),
                  discord.SelectOption(label="Max Tokens"),
                  discord.SelectOption(label="Top P"),
                  
                  
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
            case "Remove Prefix":
                await interaction.response.defer()
                await interaction.followup.send(view=RemovePrefixView(self.cb))
            case "Max Tokens":
                await interaction.response.send_modal(MTKModal(self.cb))
            case "Message History Length":
                await interaction.response.send_modal(MHLModal(self.cb))
            case "Prompt Reminder Interval":
                await interaction.response.send_modal(PRIModal(self.cb))
            case "Top P":
                await interaction.response.send_modal(TopPModal(self.cb))
            case "Add Search Prefix":
                await interaction.response.send_modal(ASPModal(self.cb))
            case "Remove Search Prefix":
                try:
                    await interaction.response.defer()
                    await interaction.followup.send(view=RSPView(self.cb))
                except Exception as e:
                    print(e)
            case "Include Usernames":
                await interaction.response.defer()
                await interaction.followup.send(view=IUMenu(self.cb))
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
        
    response = ui.TextInput(label="", style=discord.TextStyle.long, placeholder="Act as a snarky, witty, short-tempered AI named Jarvis. Only respond how Jarvis would.")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setPrompt(self.response.value):
            self.cb.context.clear()
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "prompt", self.cb.prompt)
            embed = discord.Embed(title=f"Prompt changed for {self.cb.name}", description=self.cb.prompt, color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Please try again", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
    
class IMModal(ui.Modal, title="Enter Message to Insert"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb

    content = ui.TextInput(label="Message", style=discord.TextStyle.long, placeholder="user: What's my name?\nsystem: User's name is bongo.\nassistant: Why, it's bongo, of course!")
    async def on_submit(self, interaction: discord.Interaction):
        lines = self.content.value.strip().split("\n")
        linesAdded = 0
        for line in lines:
            line = line.split(":", 1)
            ctxrole = line[0].strip().lower()
            if ctxrole == "assistant" or ctxrole == "user" or ctxrole == "system": 
                self.cb.context.append({'role':ctxrole, 'content': line[1].strip()})
                linesAdded += 1
            else:
                embed = discord.Embed(title=f"Error", description=f"Invalid role entered\nPossible roles: \"system\", \"assistant\", or \"user\"\nMessages must be in format: role: message", color=discord.Colour.blue())
                if linesAdded != 0:
                    del self.cb.context[-1 * linesAdded:]
                await interaction.response.send_message(embed=embed)
        
        embed = discord.Embed(title=f"Successfully Inserted Message", description=f"Inserted messages into {self.cb.name}'s chat history", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed)
        
class TempModal(ui.Modal, title="Enter New Temperature"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.9")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.settemp(self.response.value):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "temperature", self.cb.temperature)
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
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.7")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setpp(self.response.value):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "presence_penalty", self.cb.top_p)
            embed = discord.Embed(title=f"Presence Penalty changed for chatbot: {self.cb.name}", description="Changed to:", color=discord.Colour.blue())
            embed.add_field(name="", value=str(self.cb.presence_penalty))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Enter a number between -2.0 and 2.0\n(Example: 0.7)", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class FPModal(ui.Modal, title="Enter New Frequency Penalty"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    response = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="0.7")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.setfp(self.response.value):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "frequency_penalty", self.cb.frequency_penalty)
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
        
    prefix = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="Hey chatbot, ")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.addprefix(self.prefix.value):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "prefixes", self.cb.prefixes)
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
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "max_tokens", self.cb.max_tokens)
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
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "max_message_history_length", self.cb.max_message_history_length)
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
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "prompt_reminder_interval", self.cb.prompt_reminder_interval)
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
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "top_p", self.cb.top_p)
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
        await self.server.set_allowed_roles([role.id for role in self.values])
        # await change_server_setting_in_db(interaction.guild.id, "allowedroles", self.server.allowedroles)
        out = "\n".join([role.name for role in self.values])
        embed = discord.Embed(title=f"Allowed roles", description=f"The following roles can now interact with Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed) 

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
        AllowRoles = [interaction.guild.get_role(roleid) for roleid in self.server.allowedroles]
        for role in AllowRoles:
            if role.name in self.values:
                self.server.allowedroles.remove(role.id)
        # await change_server_setting_in_db(interaction.guild.id, "allowedroles", self.server.allowedroles)
        out = "\n".join([rolename for rolename in self.values])
        embed = discord.Embed(title=f"Removed roles", description=f"The following roles can no longer interact with Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed) 

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
       self.server = server
       super().__init__(placeholder="Select Roles to Select as Admin", min_values=1, max_values=25)
    
    async def callback(self, interaction: discord.Interaction):
        await self.server.set_admin_roles([role.id for role in self.values])
        # await change_server_setting_in_db(interaction.guild.id, "adminroles", self.server.adminroles)
        out = "\n".join([role.name for role in self.values])
        embed = discord.Embed(title=f"Admin roles", description=f"The following roles can now change the settings of Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed) 
   

class RAARDropdown(ui.Select):
    def __init__(self, interaction, server):
       options = [discord.SelectOption(label=interaction.guild.get_role(roleid).name) for roleid in server.adminroles]
       self.server = server
       super().__init__(placeholder="Select Admin Role(s) to Remove", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        AdminRoles = [interaction.guild.get_role(roleid) for roleid in self.server.adminroles]
        for role in AdminRoles:
            if role.name in self.values:
                self.server.adminroles.remove(role.id)
        # await change_server_setting_in_db(interaction.guild.id, "adminroles", self.server.adminroles)
        out = "\n".join([rolename for rolename in self.values])
        embed = discord.Embed(title=f"Removed roles", description=f"The following roles can no longer change the settings of Dis.AI chatbots:\n{out}", color=discord.Colour.blue())
        await interaction.response.send_message(embed=embed) 
 

class RAARView(ui.View):
    def __init__(self, interaction, server):
        super().__init__()
        self.add_item(RAARDropdown(interaction, server))
        
class ASPModal(ui.Modal, title="Add New Prefix"):
    def __init__(self, cb):
        super().__init__()
        self.cb = cb
        
    prefix = ui.TextInput(label="", style=discord.TextStyle.short, placeholder="search")
    async def on_submit(self, interaction: discord.Interaction):
        if self.cb.addsearchprefix(self.prefix.value):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "search_prefixes", self.cb.search_prefixes)
            embed = discord.Embed(title=f"Added search prefix for chatbot: {self.cb.name}", description=f"{self.cb.name} will now perform a search if a message starts with one of the following prefixes:", color=discord.Colour.blue())
            embed.add_field(name="", value=", ".join(self.cb.search_prefixes))
            await interaction.response.send_message(embed=embed) 
        else:
            embed = discord.Embed(title="Error", description="Please try again.", color=discord.Colour.red())
            await interaction.response.send_message(embed=embed) 
            
class RSPView(ui.View):
    def __init__(self, cb):
        super().__init__()
        self.add_item(RSPDropdown(cb))
            
            
class RSPDropdown(ui.Select):
    def __init__(self, cb):
        self.cb = cb
        options =[discord.SelectOption(label=searchprefix) for searchprefix in cb.search_prefixes]
        super().__init__(placeholder="Select Search Prefixes to Delete", options=options, min_values=1, max_values=len(options))
    
    async def callback(self, interaction: discord.Interaction):
        self.disabled = True
        for searchprefix in self.values:
            self.cb.search_prefixes.remove(searchprefix)
        
        # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "search_prefixes", self.cb.search_prefixes)
        outstr = '\n'.join(self.values)
        embed = discord.Embed(title=f"Deleted prefixes", description=f"Deleted the following search prefixes:\n{outstr}", colour=Colour.blue())
        await interaction.response.send_message(embed=embed)
            
class IUMenu(discord.ui.View):
    def __init__(self, cb):
        super().__init__()
        self.value = None
        self.cb = cb 
    
    @discord.ui.button(label="Enabled", style=discord.ButtonStyle.green)
    async def enableiu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cb.set_include_usernames(True):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "include_usernames", self.cb.include_usernames)
            embed = discord.Embed(title=f"Include usernames enabled for {self.cb.name}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed)
        
    @discord.ui.button(label="Disabled", style=discord.ButtonStyle.red)
    async def disableiu(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.cb.set_include_usernames(False):
            # await change_cb_setting_in_db(interaction.guild.id, self.cb.name, "include_usernames", self.cb.include_usernames)   
            embed = discord.Embed(title=f"Include usernames disabled for {self.cb.name}", color=discord.Colour.blue())
            await interaction.response.send_message(embed=embed)
            
class OpenAIKeyModal(ui.Modal, title="Set OpenAI API Key"):
    def __init__(self, server):
        super().__init__()
        self.server = server
        
    response = ui.TextInput(label="API Key")
    async def on_submit(self, interaction: discord.Interaction):
        try:
            complete = await self.server.set_openai_key(self.response.value)
            if complete:
                await change_server_setting_in_db(self.server.id, "openai_key", str(self.server.openai_key))
                embed=discord.Embed(title="Successfully Set API key", color=Colour.blue())
                await interaction.response.send_message(embed=embed)
            else:
                print("its inval")
                embed=discord.Embed(title="Invalid key", color=Colour.red())
                await interaction.response.send_message(embed=embed)
        except Exception as e:
            print(e)