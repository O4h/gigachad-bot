import discord
import os
import asyncio
import jishaku
import topgg

from discord.ext import commands
from discord_slash import SlashCommand
from cogs.prefix import get_prefix
from util.help import CustomHelp

default_intents = discord.Intents.default()
intents = discord.Intents(messages=True, guilds=True)


class GigaChad(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=get_prefix,
                         help_command=CustomHelp(),
                         case_insensitive=True,
                         strip_after_prefix=True,
                         activity=discord.Activity(type=discord.ActivityType.listening,
                                                   name="@Giga Chad help"),
                         intents=intents)

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print(discord.__version__)
        print('------')


gigachad = GigaChad()

slash = SlashCommand(gigachad, sync_commands=True, sync_on_cog_reload=True)

topggcli = topgg.DBLClient(bot=gigachad, token=os.getenv("TOPGG_TOKEN"), autopost=True)


for filename in os.listdir('./cogs'):
    if filename.endswith(".py") and not filename.startswith("_"):
        gigachad.load_extension(f"cogs.{filename[:-3]}")
gigachad.load_extension("jishaku")

gigachad.run(os.getenv("TOKEN"))
