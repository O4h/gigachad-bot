import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from cogs.prefix import get_prefix

default_intents = discord.Intents.default()
intents = discord.Intents(messages=True, guilds=True)


class GigaChad(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix, intents=intents)

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print(discord.__version__)
        print('------')
        await gigachad.change_presence(activity=discord.Game(name="Type gc!help for help"))


gigachad = GigaChad()

gigachad.remove_command('help')

slash = SlashCommand(gigachad, sync_commands=True, sync_on_cog_reload=True)

for filename in os.listdir('./cogs'):
    if filename.endswith(".py") and not filename.startswith("_"):
        gigachad.load_extension(f"cogs.{filename[:-3]}")

load_dotenv()
gigachad.run(os.getenv("TOKEN"))
