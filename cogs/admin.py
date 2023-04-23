import discord
from discord.ext import commands
from extensions import lists
from utils import jsonhandler
from datetime import datetime, timedelta
class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_ready(self):
        print("AdminCommands cog loaded.")

    # to be removed. temporary message to users.
    @commands.command(name='sendmsg')
    async def sendmsg(self, ctx, serverid, channelid, msg):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        server = self.bot.get_guild(int(serverid))
        channels = server.channels
        for channelz in channels:
            print(f"Name: {channelz.name} id: {channelz.id}")
        channel = server.get_channel(int(channelid))
        embed = discord.Embed(title="[System Notice]", description = msg, color=discord.Colour.blue())
        await channel.send(embed=embed)
        
    @commands.command(name='removectxs')
    async def removectxs(self, ctx):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        print("starting")
        try:
            for guild in self.bot.guilds:
                for cb in lists.bot_instances[guild.id]:
                    await jsonhandler.change_cb_setting_in_db(guild.id, cb.name, "context", [])
                    
            await jsonhandler.load_db_to_mem(self.bot.guilds)
        except Exception as e:
            print("removectx err")
            print(e)
        print("finished")
        
    @commands.command(name='defprompts')
    async def defprompts(self, ctx):
        if ctx and not ctx.author.id == 215199288177721344:
            return

        print("starting")
        try:
            for guild in self.bot.guilds:
                for cb in lists.bot_instances[guild.id]:
                    await jsonhandler.change_cb_setting_in_db(guild.id, cb.name, "prompt", "Act as a snarky, sarcastic, arrogant, witty AI assistant named Jarvis. Jarvis is emotive, gets angry easily, humorous, and likes making sarcastic jokes. He treats everything like a joke. He is very ironic in his responses. Only respond how Jarvis would.")
                    
            await jsonhandler.load_db_to_mem(self.bot.guilds)
        except Exception as e:
            print("defprompt err")
            print(e)
        print("finished")
                
    @commands.command(name='addguildsetting')
    async def addguildsetting(self, ctx, setting, newvalue=""):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        print("adding db setting")
        setting = str(setting.strip())
        newvalue = newvalue.strip()
        try:
            newvalue = int(newvalue)
        except Exception as e:
            print(e)
            
        if newvalue == "current_time":
            now = now = datetime.now().replace(microsecond=0)
            date_format = "%Y-%m-%d %H:%M:%S"
            newvalue = now.strftime(date_format)

        print(f".{setting}.{newvalue}.")
        try:
            await jsonhandler.new_server_setting(setting, newvalue)
        except Exception as e:
            print(f"addguildsetting err: {e}")
            
        print("done")
        
    @commands.command(name='stats')
    async def stats(self, ctx):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        out = ""
        for guild in self.bot.guilds:
            server = await jsonhandler.get_server(guild.id)
            out += f"\n\n{guild.name} ({server.id}) dailymsgs({server.dailymsgs})\nChatbots:\\nn"
            for chatbot in lists.bot_instances[server.id]:
                out += f"Name: {chatbot.name}\nPrompt: {chatbot.prompt}\nContext: {chatbot.context}\n"
                
        print(out)
        
    @commands.command(name='purgedb')
    async def purgedb(self, ctx):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        await jsonhandler.purgedb(self.bot)
        
    @commands.command(name='setbotsetting')
    async def setbotsetting(self, ctx, botname, setting, value):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        print("starting")
        try:
            value = int(value)
        except Exception as e:
            print(e)
            
        if value == "emptylist":
            value = []
            value.clear()
        
        for guild in self.bot.guilds:
            for bot in lists.bot_instances[guild.id]:
                if bot.name == botname:
                    await jsonhandler.change_cb_setting_in_db(guild.id, botname, setting, value)
                    
        print("done. restart.")
        
    @commands.command(name='addbotsetting')
    async def addbotsetting(self, ctx, setting, value):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        print("starting")
        try:
            value = int(value)
        except Exception as e:
            print(e)
            
            
        if value == "emptylist":
            value = []
            value.clear()
            
        
        
        for guild in self.bot.guilds:
            for bot in lists.bot_instances[guild.id]:
                await jsonhandler.change_cb_setting_in_db(guild.id, bot.name, setting, value)
                    
        print("done. restart.")
        
        
        
    @commands.command(name='comparedates')
    async def comparedates(self, ctx, seconds, should_leave):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        now = datetime.now()
        seconds=int(seconds)
        if should_leave == "true":
            should_leave = True
        else: 
            should_leave = False
        for server in lists.servers:
            time_diff = now - server.last_interaction_date
            if time_diff.total_seconds() > seconds:
                guild = await self.bot.fetch_guild(server.id)
                print(f"Going to leave guild: {guild.name} - {time_diff} seconds")
                if should_leave:
                    await guild.leave()
            
            
            
        
    
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
