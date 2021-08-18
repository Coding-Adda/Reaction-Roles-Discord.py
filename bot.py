from discord.ext import commands

bot = commands.Bot("!")


@bot.event
async def on_ready():
    print("I am ready!")


bot.load_extension("cogs.reaction-roles")

bot.run("ODI3NDE4Mjc0ODc4NzE3OTY0.YGavUQ.dTUlotCriVDzGutJLuad2hJG99M")
