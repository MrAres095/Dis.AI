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
    async def sendmsg(self, ctx, serverid, channelid):
        if ctx and not ctx.author.id == 215199288177721344:
            return
        server = self.bot.get_guild(int(serverid))
        channels = server.channels
        for channelz in channels:
            print(channelz.name)
        channel = server.get_channel(int(channelid))
        embed = discord.Embed(title="[System Notice]", description = "Dis.AI has updated to v1.1. As a result of major backend changes, all data has been reset. Please use the following to set up a new chatbot: ```/createchatbot```\n\n**New feature:** chatbots now have web search abilities. Prefix your message with \"search\" to tell the chatbot to retrieve info from the web.\nFor example: ```search who the newest valorant agent is```Add or remove search prefixes with /settings\n\nThis will be the last notice of this kind.", color=discord.Colour.blue())
        await channel.send(embed=embed)
async def setup(bot):
    await bot.add_cog(AdminCommands(bot))