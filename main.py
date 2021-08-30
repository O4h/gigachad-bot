import asyncio
import os

import asyncpg
import discord
import jishaku
from cogs.prefix import get_prefix
from discord.ext import commands
from discord_slash import SlashCommand
from util.help import CustomHelp

intents = discord.Intents(messages=True, guilds=True)

# the initial sql query, to add tables
sql_query = "CREATE TABLE IF NOT EXISTS prefixes(guild BIGINT PRIMARY KEY, prefix VARCHAR(125));" \
            "CREATE TABLE IF NOT EXISTS lang(guild BIGINT PRIMARY KEY, lang VARCHAR(2));" \
            "CREATE TABLE IF NOT EXISTS commands_logs(time INT NOT NULL, guild BIGINT, cmd VARCHAR(25), usr BIGINT, type INT);" \
            "CREATE TABLE IF NOT EXISTS guilds_logs(time INT NOT NULL, guild BIGINT, joined BOOLEAN)"


async def run():
    """ The function to run the bot, required cuz async stuff annoying basically"""

    credentials = {"user": os.getenv("DB_USER"), "password": os.getenv("DB_PASSWORD"),
                   "database": os.getenv("DB_DATABASE"),
                   "host": os.getenv("DB_HOST"), "port": os.getenv("DB_PORT")}

    # make the connection to the db
    db = await asyncpg.create_pool(**credentials)

    # initiate tables and fetch cache
    async with db.acquire() as conn:
        await conn.execute(sql_query)
        prefix_data = await conn.fetch("SELECT * FROM prefixes")
        lang_data = await conn.fetch("SELECT * FROM lang")

    # load the bot class
    gigachad = GigaChad(db=db, prefix_cache=dict(prefix_data), lang_cache=dict(lang_data))

    # load the slash commands class
    slash = SlashCommand(gigachad, sync_commands=True, sync_on_cog_reload=True)

    # load cogs
    for filename in os.listdir('./cogs'):

        if filename.endswith(".py") and not filename.startswith("_"):
            gigachad.load_extension(f"cogs.{filename[:-3]}")

    gigachad.load_extension("jishaku")

    # and finally, start the bot!
    await gigachad.start(os.getenv("TOKEN"))


class GigaChad(commands.Bot):
    def __init__(self, db, prefix_cache: dict, lang_cache: dict):
        """" the bot class, used everywhere.
        :param db: is passed for easier use, same for
        :param prefix_cache: & :param lang_cache:
        """
        super().__init__(
            command_prefix=get_prefix,
            help_command=CustomHelp(),
            case_insensitive=True,
            strip_after_prefix=True,
            activity=discord.Activity(
                type=discord.ActivityType.listening,
                name="@Giga Chad help"
            ),
            intents=intents
        )

        self.db = db
        self.prefix_cache = prefix_cache
        self.lang_cache = lang_cache
        self.invite_link = "https://discord.com/api/oauth2/authorize?client_id=843550872293867570&permissions=379904&scope=bot%20applications.commands"

    async def on_ready(self):
        print('------')
        print('Logged in as')
        print(self.user.name)
        print(self.user.id)
        print(discord.__version__)
        print('------')

    async def reload_cache(self, table: str):
        """ Reload prefix or lang cache at runtime
        :param table: can either be "prefixes" or "lang"
        """
        async with self.db.acquire() as conn:
            if table == "prefixes":
                data = await conn.fetch("SELECT * FROM prefixes")
                self.prefix_cache = dict(data)
                print("Prefix cache loaded")
            elif table == "lang":
                data = await conn.fetch("SELECT * FROM lang")
                self.lang_cache = dict(data)
                print("Lang cache loaded")


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
