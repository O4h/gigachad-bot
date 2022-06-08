import asyncio
import os
import asyncpg
import disnake
import jishaku
import sentry_sdk

from disnake.ext import commands

intents = disnake.Intents(messages=True, guilds=True)

# the initial sql query, to add tables
sql_query = (
    "CREATE TABLE IF NOT EXISTS commands_logs(time INT NOT NULL, guild BIGINT, cmd VARCHAR(25), usr BIGINT, type INT);"
    "CREATE TABLE IF NOT EXISTS guilds_logs(time INT NOT NULL, guild BIGINT, joined BOOLEAN, guild_count INT);"
    "CREATE TABLE IF NOT EXISTS commands_stats_total(time INT NOT NULL, gigachadify INT, meme INT, chadmeter INT, caption INT)"
)

# Init sentry
if os.getenv("BETA") != "TRUE":
    sentry_sdk.init(os.getenv("SENTRY_ENDPOINT"), traces_sample_rate=1.0)


async def run():
    """
    Main function, runs the bot.
    """
    # make the connection to the db
    url = f"postgres://" \
          f"{os.getenv('DB_USER')}:" \
          f"{os.getenv('DB_PASSWORD')}" \
          f"@{os.getenv('DB_HOST')}:" \
          f"{os.getenv('DB_PORT')}/{os.getenv('DB_DATABASE')}"
    db = await asyncpg.create_pool(dsn=url)

    # load the bot class
    bot = Bot(db=db)

    # load cogs
    for filename in os.listdir('./cogs'):

        if filename.endswith(".py") and not filename.startswith("_"):
            bot.load_extension(f"cogs.{filename[:-3]}")

    bot.load_extension("jishaku")
    # and finally, start the bot!
    await bot.start(os.getenv("TOKEN"))


class Bot(commands.AutoShardedBot):
    def __init__(self, db: asyncpg.pool.Pool) -> None:
        """ "
        The Bot object

        Parameters
        ----------
        db: asyncpg.pool.Pool
            The database connection
        """
        super().__init__(
            command_prefix="gc!",
            # only usable in dms without the message content intent
            case_insensitive=True,
            strip_after_prefix=True,
            activity=disnake.Activity(
                type=disnake.ActivityType.listening, name="slash commands"
            ),
            help_command=None,
            intents=intents,
        )

        self.db = db
        self.invite_link = "https://discord.com/api/oauth2/authorize?client_id=843550872293867570&permissions=379904" \
                           "&scope=bot%20applications.commands "
        self.command_list = {
            "meme": ["meme"],
            "gigachadify": ["gigachadify", "Gigachadify"],
            "chadmeter": ["chadmeter", "Chadmeter"],
            "caption": ["caption"],
        }

    async def on_ready(self) -> None:
        print("------")
        print("Logged in as")
        print(self.user.name)
        print(self.user.id)
        print(disnake.__version__)
        print("------")


loop = asyncio.get_event_loop()
loop.run_until_complete(run())
