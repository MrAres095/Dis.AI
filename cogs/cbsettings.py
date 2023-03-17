import discord
from discord.ext import commands
import json
import lists
import ChatBot
from jsonhandler import *
from discord import Colour

# commands that change a chatbot's settings
class ChatBotSettings(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # events
    @commands.Cog.listener()
    async def on_ready(self):
        print("ChatBotSettings cog loaded.")
        
    # commands
    @commands.command()
    async def listbots(self, ctx) -> None:
        embed = discord.Embed(title="List of chatbots", colour=Colour.blue())
        for bot in lists.bot_instances[str(ctx.guild.id)]:
            embed.add_field(name=bot.name, value="", inline=False)
        await ctx.send(embed=embed)
    
    
    @commands.command()
    async def botinfo(self, ctx, botname) -> None:
        cb = await get_cb(ctx, botname)
        if not cb:
            embed = discord.Embed(title="Error. Bot does not exist.", description="Please make sure you have entered the name correctly", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        try:
            channels = [self.bot.get_channel(channel_id).name for channel_id in cb.channels]
            out = f"""
            **Name:** {cb.name}
**Prompt:** {cb.prompt}
**Enabled:** {cb.enabled}
**Allowed Channels:** {", ".join(channels)}
**Prefixes:** {", ".join(cb.prefixes)}
**Max Tokens:** {cb.max_tokens}
**Temperature:** {cb.temperature}
**Presence Penalty:** {cb.presence_penalty}
**Frequency Penalty:** {cb.frequency_penalty}
**Top P:** {cb.top_p}
**Max Message History Length:** {cb.max_message_history_length}
**Prompt Reminder Interval:** {cb.prompt_reminder_interval}
            """
            max_msgs = (len(out) // 2000) + 1
            if max_msgs > 1:
                for i in range(max_msgs):
                    await ctx.send(out[i*1990:(i+1)*1990] + f" ({i + 1}/{max_msgs})")
            else:
                await ctx.send(out)
        except Exception as e:
            print(e)
            
    @commands.command()
    async def setdefault(self, ctx, botname) -> None:
        cb = await get_cb(ctx, botname)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        defbot = ChatBot.ChatBot(name=cb.name)
        cb = defbot
        await update_bot_json(ctx.guild.id, cb)
        embed = discord.Embed(title=f"Successfully Reset Chatbot", description=f"All settings for {cb.name} has been reset to default\nai.botinfo {cb.name} to see its settings.", colour=Colour.blue())
        await ctx.send(embed=embed)
        

    @commands.command(aliases=['nc'])
    async def newchat(self, ctx, *args) -> None:
        if len(args) > 1:
            embed = discord.Embed(title=f"New Chat Error", description="The chatbot name should not have have any spaces. Please try again\nExample: \nai.newchat Storywriter", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        elif len(args) < 1:
            embed = discord.Embed(title=f"New Chat Error", description="Please enter a valid name for the chatbot.\nExample: \nai.newchat Storywriter", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        with open('data.json', 'r') as f:
            data = json.load(f)
            for bot in data[str(ctx.guild.id)]['bots']:
                if bot['name'].strip().lower() == args[0].strip().lower():
                    embed = discord.Embed(title=f"New Chat Error", description=f"A chatbot with this name already exists. Please pick a different name and try again.", colour=Colour.blue())
                    await ctx.send(embed=embed)
                    return
        
        newbot = ChatBot.ChatBot(name=args[0].strip(), server_id=ctx.guild.id, channels = [])
        lists.bot_instances[str(ctx.guild.id)].append(newbot)
        if not newbot.setName("".join(args)):
            embed = discord.Embed(title="Please choose a different name and try again.", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(newbot))
        try:
            embed = discord.Embed(title=f"New Chat Created: {newbot.name}", colour=Colour.blue())
            embed.add_field(name=f"Use 'ai.channeladd {newbot.name}' to add it to the current channel\nUse 'ai.prompt {newbot.name} [prompt]' to change the prompt (default prompt: Jarvis)", 
                            value="See ai.help for more configurable settings!")
            await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            
    @commands.command()
    async def deletechat(self, ctx, name=None):
        cb = await get_cb(ctx, name)
        if not cb or not name:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example\nai.deletechat Storywriter", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        try:
            print("trying success")
            success = await delete_bot_json(ctx.guild.id, await make_bot_dict(cb))
            print("done with success")
            if success:
                botname = cb.name
                print(lists.bot_instances)
                lists.bot_instances[str(ctx.guild.id)].remove(cb)
                print("supa succe")
                embed = discord.Embed(title=f"{botname} successfully deleted", colour=Colour.blue())
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"Invalid name. Please try again", description="Example\nai.deletechat Storywriter", colour=Colour.blue())
                await ctx.send(embed=embed)
                
                
        except Exception as e:
            print(e)
            
        
    @commands.command()
    async def prompt(self, ctx, name=None, *prompt) -> None:
        if not name:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.prompt Storywriter You are a story writing AI. You write stories with the given outline with an exposition, conflict, climax, and resolution. Use beautiful, poetic, and descriptive prose.", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.prompt Storywriter You are a story writing AI. You write stories with the given outline with an exposition, conflict, climax, and resolution. Use beautiful, poetic, and descriptive prose.", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.setPrompt(" ".join(prompt)):
            embed = discord.Embed(title="Invalid prompt. Please try again.", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            cb.context.clear()
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Prompt changed for {cb.name}", description="Prompt is now:")
            embed.add_field(name="", value=cb.prompt)
            await ctx.send(embed=embed)    

    @commands.command(aliases=["mtk"])
    async def maxtokens(self, ctx, name=None, max_tokens=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example\nai.mtk 1000", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.setmaxtk(max_tokens):
            embed = discord.Embed(title=f"Max tokens should be between 0 and 4096", description="Example:\nai.mtk Storywriter 1000", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Max output tokens changed for {cb.name}", description=f"Max Tokens is now: {cb.max_tokens}", colour=Colour.blue())
            await ctx.send(embed=embed)

    @commands.command(aliases=["temp"])
    async def temperature(self, ctx, name=None, temperature=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.temp Storywriter 0.7", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.settemp(temperature):
            embed=discord.Embed(title="Temperature should be between 0.0 and 2.0.", description="Example:\nai.temp Storywriter 0.7", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Temperature changed for {cb.name}", description="Temperature is now:", colour=Colour.blue())
            embed.add_field(name="", value=str(cb.temperature))
            await ctx.send(embed=embed)

    @commands.command()
    async def top_p(self, ctx, name=None, top_p=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.top_p Storywriter 1.0",colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.settopp(top_p):
            embed = discord.Embed(title=f"Top P should be between 0.0 and 1.0", description="Example:\nai.top_p Storywriter 1.0", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Top P changed for {cb.name}", description="Top P is now:", colour=Colour.blue())
            embed.add_field(name="", value=str(cb.top_p))
            await ctx.send(embed=embed)
            

    @commands.command()
    async def n_obf(self, ctx, name, n) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again")
            await ctx.send(embed=embed)
            return
        if not cb.setn(n): 
            await ctx.send("N should be a whole number greater than 1.")
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"N changed for {cb.name}", description="N is now:")
            embed.add_field(name="", value=str(cb.n))
            await ctx.send(embed=embed)

    @commands.command(aliases=['pp'])
    async def presencepenalty(self, ctx, name=None, presence_penalty=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.pp Storywriter 0.3", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.setpp(presence_penalty):
            embed = discord.Embed(title=f"Presence penalty must be between -2.0 and 2.0.", description="Example:\nai.pp Storywriter 0.3", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Presence penalty changed for {cb.name}", description="Presence penalty is now:")
            embed.add_field(name="", value=str(cb.presence_penalty))
            await ctx.send(embed=embed)

    @commands.command(aliases=['fp'])
    async def frequencypenalty(self, ctx, name=None, frequency_penalty=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.fp Storywriter 0.8",colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.setfp(frequency_penalty):
            embed = discord.Embed(title="Frequency penalty must be between -2.0 and 2.0", description="Example:\nai.fp Storywriter 0.8", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Frequency penalty changed for {cb.name}", description="Frequency penalty is now: ", colour=Colour.blue())
            embed.add_field(name="", value=str(cb.frequency_penalty))
            await ctx.send(embed=embed)

    @commands.command()
    async def enabled(self, ctx, name=None, enabled=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.enabled Storywriter true",colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        enabled = enabled.lower()
        if enabled == "true" or enabled == 't':
            enabled = True
            msgstr = "Enabled"
        elif enabled == "false" or enabled == 'f':
            enabled = False
            msgstr = "Disabled"
        else:
            embed = discord.Embed(title=f"Enabled must be true or false. ", description="Example:\nai.enabled Storywriter false", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        
        if not cb.set_enabled(enabled):
            embed = discord.Embed(title=f"Enabled must be true or false. ", description="Example:\nai.enabled Storywriter false", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Activity changed for {cb.name}", description=f"{cb.name} is now:",colour=Colour.blue())
            embed.add_field(name="", value=msgstr)
            await ctx.send(embed=embed)

    @commands.command(aliases=["mmhl"])
    async def maxmessagehistorylength(self, ctx, name=None, mmhl=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description=f"Example:\nai.maxmessagehistorylength Storywriter 20", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.set_mmhl(mmhl):
            embed = discord.Embed(title=f"Max message history length must be greater than 0.", description=f"Example:\nai.maxmessagehistorylength Storywriter 20", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Max context questions changed for {cb.name}", description="Max context questions is now:", colour=Colour.blue())
            embed.add_field(name="", value=str(cb.max_message_history_length))
            await ctx.send(embed=embed)
            
    @commands.command()
    async def channeladd(self, ctx, botname=None) -> None:
        try:
            cb = await get_cb(ctx, botname)
            if not cb:
                embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.channeladd Storywriter", colour=Colour.blue())
                await ctx.send(embed=embed)
                return
            if ctx.channel.id not in cb.channels:  
                cb.channels.append(ctx.channel.id)
                await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
                embed = discord.Embed(title=f"{cb.name} has been added to the current channel", colour=Colour.blue())
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{cb.name} has already been added to the current channel", colour=Colour.blue())
                await ctx.send(embed=embed)
        except Exception as e:
            print(e)
            
    @commands.command()
    async def channelremove(self, ctx, botname=None) -> None:
            cb = await get_cb(ctx, botname)
            if not cb:
                embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.channelremove Storywriter", colour=Colour.blue())
                await ctx.send(embed=embed)
                return
            cb.channels.remove(ctx.channel.id)
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"{cb.name} has been removed from the current channel", colour=Colour.blue())
            await ctx.send(embed=embed)
            
    @commands.command(aliases=["pri"])
    async def promptreminderinterval (self, ctx, name=None, pri=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.pri Storywriter 10", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.set_pri(pri):
            embed = discord.Embed(title=f"Prompt reminder interval must be 0 or greater.", description="Example:\nai.pri Storywriter 10", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            embed = discord.Embed(title=f"Prompt reminder interval changed for {cb.name}", description="Context reminder interval is now:", colour=Colour.blue())
            embed.add_field(name="", value=str(cb.prompt_reminder_interval))
            await ctx.send(embed=embed)


    @commands.command(aliases=["iu"]) # need to simplify this code later
    async def includeusernames(self, ctx, name=None, include_usernames=None) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.iu Storywriter false", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if include_usernames:
            include_usernames = include_usernames.lower()
        if include_usernames == "true" or include_usernames == 't':
            include_usernames = True
        elif include_usernames == "false" or include_usernames == 'f':
            include_usernames = False
        else:
            embed = discord.Embed(title=f"Include usernames must be true of false", description="Example:\nai.iu Storywriter false", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not cb.set_include_usernames(include_usernames):
            embed = discord.Embed(title=f"Include usernames must be true of false", description="Example:\nai.iu Storywriter false", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        else:
            await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
            if cb.include_usernames:
                msgstr = "Enabled"  
            elif not cb.include_usernames:
                msgstr = "Disabled"
            else:
                await ctx.send("Error")
            embed = discord.Embed(title=f"Include usernames changed for {cb.name}", description=f"Include usernames is now:", colour=Colour.blue())
            embed.add_field(name="", value=str(msgstr))
            await ctx.send(embed=embed)

    @commands.command(aliases=["rmh"])
    async def resetmessagehistory(self, ctx, name=None, *msgs_to_delete) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.rmh Storywriter 4", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        try:
            msgs_to_delete = int(msgs_to_delete[0])
            if msgs_to_delete <= 0:
                embed = discord.Embed(title=f"Enter a number greater than 0.", description="Example:\nai.rmh Storywriter 4", colour=Colour.blue())
                await ctx.send(embed=embed)
            else:   
                del cb.context[(-1 * msgs_to_delete):]
                embed = discord.Embed(title=f"Reset message history for {cb.name}", description=f"{msgs_to_delete} messages deleted", colour=Colour.blue())
                await ctx.send(embed=embed)
        except Exception as e:
            ctxlen = len(cb.context)
            cb.context.clear()
            embed = discord.Embed(title=f"Reset message history for {cb.name}", description=f"{ctxlen} messages deleted", colour=Colour.blue())
            await ctx.send(embed=embed)
            
    @commands.command(aliases=["ap"])
    async def addprefix(self, ctx, name=None, *prefix) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.ap Storywriter Hey storywriter", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        prefix = " ".join(prefix)
        prefix = prefix.strip().lower()
        cb.add_prefix(prefix)
        await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
        embed = discord.Embed(title=f"Added prefix for {cb.name}", description=f"Prefix: {prefix}", colour=Colour.blue())
        await ctx.send(embed=embed)

    @commands.command(aliases=["rp"])
    async def removeprefix(self, ctx, name=None, *prefix) -> None: 
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.rp Storywriter Hey storywriter", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if len(prefix) < 1:
            cb.prefixes.clear()
            embed = discord.Embed(title=f"Removed prefixes for {cb.name}", description=f"All prefixes have been removed", colour=Colour.blue())
            await ctx.send(embed=embed)
        else:
            prefix = " ".join(prefix).strip().lower()
            if prefix in cb.prefixes:
                cb.remove_prefix(prefix)
                await update_bot_json(ctx.guild.id, await make_bot_dict(cb))
                embed = discord.Embed(title=f"Removed prefix for {cb.name}", description=f"'{prefix}' prefix has been removed", colour=Colour.blue())
                await ctx.send(embed=embed)
            else:
                embed = discord.Embed(title=f"{cb.name} does not have prefix '{prefix}'", colour=Colour.blue())
                await ctx.send(embed=embed)

    @commands.command(aliases=["im"])
    async def insertmessage(self, ctx, name=None, role=None, *msg) -> None:
        cb = await get_cb(ctx, name)
        if not cb:
            embed = discord.Embed(title=f"Invalid name. Please try again", description="Example:\nai.im Storywriter assistant The leprechaun frolicks in the scutch grass.", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
        if not role:
            embed = discord.Embed(title=f"Invalid role. Please try again", description="Example:\nai.im Storywriter assistant The leprechaun frolicks in the scutch grass.", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
            
        msg = " ".join(msg)
        role = role.strip().lower()
        if role == "user":
            cb.context.append({'role':'user','content':msg})
        elif role == "assistant":
            cb.context.append({'role':'assistant','content':msg})
        elif role == "system":
            cb.context.append({'role':'system', 'context':msg})
        else:
            embed = discord.Embed(title=f"Invalid role (Valid roles: user, assistant, system). Please try again", description="Example:\nai.im Storywriter assistant The leprechaun frolicks in the scutch grass.", colour=Colour.blue())
            await ctx.send(embed=embed)
            return
    
            
        embed = discord.Embed(title=f"Inserted {role} message for {cb.name}", description=f"Message: {msg}")
        await ctx.send(embed=embed)
    
async def setup(bot):
    await bot.add_cog(ChatBotSettings(bot))