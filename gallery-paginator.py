import discord
import datetime
from discord_slash import cog_ext, SlashContext
from discord_slash.context import InteractionContext, ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import *


class GalleryPaginator:
    def __init__(self, ctx, user):
        self.gigachad = ctx.bot
        self.user = user
        self.ctx = ctx
        self.memes_pages = []
        self.top = 0
        self.index = 1

    async def run(self):
        async with self.gigachad.db.acquire() as conn:
            memes = await conn.fetch("SELECT * FROM gallery WHERE usr = $1 ORDER BY time DESC", self.user)

        if not memes:
            pass

        else:
            for meme in memes:
                embed = discord.Embed.from_dict(meme['embed'])
                embed.set_footer(text=f"ID: {meme['id']} | Created at:")
                embed.timestamp = datetime.fromtimestamp(meme['time'])
                self.memes_pages.append(embed)

        self.top = len(self.pages)
        msg = await self.ctx.send(
            content="Test",
            embed=self.memes_pages[0],
            components=self.components()
        )
        while True:
            button_ctx = await wait_for_component(
                self.gigachad,
                components=self.components()
            )
            if button_ctx.custom_id == "prev":
                self.index = self.index - 1 or 1
            elif button_ctx.custom_id == "next":
                self.index = self.index + 1 or self.top

            await button_ctx.edit_origin(
                content="Testykgk",
                embed=self.meme_pages[self.index - 1],
                components=self.components()
            )

    def components(self) -> list:
        disableLeft = self.index == 1
        disableRight = self.index == self.top
        control_buttons = [
            create_button(
                style=ButtonStyle.blurple,
                emoji="◀",
                disabled=disableLeft,
                custom_id="prev"
            ),
            create_button(
                style=ButtonStyle.blurple,
                emoji="▶",
                disabled=disableRight,
                custom_id="next"
            )
        ]
        components = [create_actionrow(*control_buttons)]
        return components
