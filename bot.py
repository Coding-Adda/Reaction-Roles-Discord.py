from discord.ext import commands

bot = commands.Bot("!")


@bot.event
async def on_ready():
    print("I am ready!")


bot.load_extension("cogs.reaction-roles")

bot.run("YOUR_TOKEN_HERE")
