import discord
from discord.ext import commands
from extensions.lists import *
from utils.jsonhandler import change_cb_setting_in_db, load_db_to_mem
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
        print("starting")
        try:
            for guild in self.bot.guilds:
                for cb in bot_instances[guild.id]:
                    await change_cb_setting_in_db(guild.id, cb.name, "context", [])
                    
            await load_db_to_mem(self.bot.guilds)
        except Exception as e:
            print("removectx err")
            print(e)
        print("finished")
        
    @commands.command(name='defprompts')
    async def defprompts(self, ctx):
        print("starting")
        try:
            for guild in self.bot.guilds:
                for cb in bot_instances[guild.id]:
                    await change_cb_setting_in_db(guild.id, cb.name, "prompt", "Act as a snarky, sarcastic, arrogant, witty AI assistant named Jarvis. Jarvis is emotive, gets angry easily, humorous, and likes making sarcastic jokes. He treats everything like a joke. He is very ironic in his responses. Only respond how Jarvis would.")
                    
            await load_db_to_mem(self.bot.guilds)
        except Exception as e:
            print("defprompt err")
            print(e)
        print("finished")
                
        
        
    
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))
