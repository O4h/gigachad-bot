import asyncio
import os
import asyncpg
import disnake
import sentry_sdk


from disnake.ext import commands

# from discord_slash import SlashCommand
# from util.help import CustomHelp

intents = disnake.Intents(messages=True, guilds=True)

# the initial sql query, to add tables
sql_query = (
    "CREATE TABLE IF NOT EXISTS lang(guild BIGINT PRIMARY KEY, lang VARCHAR(2));"
    "CREATE TABLE IF NOT EXISTS commands_logs(time INT NOT NULL, guild BIGINT, cmd VARCHAR(25), usr BIGINT, type INT);"
    "CREATE TABLE IF NOT EXISTS guilds_logs(time INT NOT NULL, guild BIGINT, joined BOOLEAN, guild_count INT);"
    "CREATE TABLE IF NOT EXISTS commands_stats_total(time INT NOT NULL, gallery INT, gigachadify INT, meme INT, chadmeter INT, caption INT)"
)


# Init sentry
if not bool(os.getenv("BETA") == "TRUE"):
    sentry_sdk.init(os.getenv("SENTRY_ENDPOINT"), traces_sample_rate=1.0)


async def run():
    """
    Main function, runs the bot.
    """

    credentials = {
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "database": os.getenv("DB_DATABASE"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    }

    # make the connection to the db
    db = await asyncpg.create_pool(**credentials)

    # initiate tables and fetch cache
    async with db.acquire() as conn:
        await conn.execute(sql_query)
        prefix_data = await conn.fetch("SELECT * FROM prefixes")
        lang_data = await conn.fetch("SELECT * FROM lang")

    # load the bot class
    bot = Bot(db=db, lang_cache=dict(lang_data))

    #load cogs
    for filename in os.listdir('./cogs'):

        if filename.endswith(".py") and not filename.startswith("_"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    # and finally, start the bot!
    await bot.start(os.getenv("TOKEN"))


class Bot(commands.AutoShardedBot):
    def __init__(self, db, lang_cache: dict):
        """ "
        The Bot object

        Parameters
        ----------
        db: asyncpg.pool.Pool
            The database connection
        lang_cache: dict
            The language cache
        """
        super().__init__(
            command_prefix="gc!",
            # only usable in dms without the message content intent
            case_insensitive=True,
            strip_after_prefix=True,
            activity=disnake.Activity(
                type=disnake.ActivityType.listening, name="@Giga Chad help"
            ),
            intents=intents,
        )

        self.db = db
        self.lang_cache = lang_cache
        self.invite_link = "https://discord.com/api/oauth2/authorize?client_id=843550872293867570&permissions=379904&scope=bot%20applications.commands"
        self.command_list = {
            "meme": ["meme"],
            "gigachadify": ["gigachadify", "Gigachadify"],
            "chadmeter": ["chadmeter", "Chadmeter"],
            "caption": ["caption"],
            "gallery": ["gallery"],
        }

    async def on_ready(self) -> None:
        print("------")
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print(disnake.__version__)
        print("------")

    async def reload_cache(self) -> None:
        """
        Reload prefix or lang cache at runtime
        """
        async with self.db.acquire() as conn:
            data = await conn.fetch("SELECT * FROM lang")
            self.lang_cache = dict(data)
            print("Lang cache loaded")


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
