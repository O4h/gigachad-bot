import discord
import os
import asyncio
from dotenv import load_dotenv
from discord.ext import commands
from discord_slash import SlashCommand
from cogs.prefix import get_prefix
from cogs.help import CustomHelp

default_intents = discord.Intents.default()
intents = discord.Intents(messages=True, guilds=True)


class GigaChad(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         help_command=CustomHelp(),
                         case_insensitive=True,
                         strip_after_prefix=True,
                         intents=intents)

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print(discord.__version__)
        print('------')
        await gigachad.change_presence(activity=discord.Activity(type=discord.ActivityType.listening,
                                                                 name="@Giga Chad help"))


gigachad = GigaChad()

slash = SlashCommand(gigachad, sync_commands=True, sync_on_cog_reload=True)


for filename in os.listdir('./cogs'):
    if filename.endswith(".py") and not filename.startswith("_") and not filename.startswith("help"):
        gigachad.load_extension(f"cogs.{filename[:-3]}")

load_dotenv()
gigachad.run(os.getenv("TOKEN"))
