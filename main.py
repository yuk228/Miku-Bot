import os
import nextcord
from dotenv import load_dotenv
from nextcord.ext import commands

bot = commands.Bot(command_prefix="!", intents=nextcord.Intents.all())

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")
    print(f'Bot ID: {bot.user.id}')
    await bot.change_presence(activity=nextcord.Game(name="/help"))

if __name__ == "__main__":
    load_dotenv()
    bot.load_extension("slash_commands")
    bot.run(os.getenv("TOKEN"))