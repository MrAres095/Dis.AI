import discord
from discord.ext import commands
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
        
        
    
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))