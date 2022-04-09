from typing import Union, Optional
from PIL import Image, ImageDraw
from io import BytesIO

import json
import os
import random
import asyncio
import aiohttp

import disnake
from disnake.ext import commands

from util.misc import get_emote, create_embed, has_voted
from util.misc import translate as _

IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")  # load env variables
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

caption_templates = json.loads(open("ressources/caption_templates.json").read())


class Fun(commands.Cog):
    """
    Fun stuff goes here!
    Commands that are both slash and context menu are executed outside of the class.
    """

    def __init__(self, bot: commands.AutoShardedBot) -> None:
        self.bot = bot

    @commands.slash_command(name="meme")
    async def meme(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        subreddit: Optional[str] = None,
    ) -> None:
        """
        🎲 Get a random meme!

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        subreddit : str, optional
            Get a meme from a particular subreddit
        """
        url = (
            f"https://meme-api.herokuapp.com/gimme/{subreddit}"
            if subreddit
            else "https://meme-api.herokuapp.com/gimme"
        )

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as r:
                data = await r.read()

        if r.status != 200:
            await error_api(ctx)
            return

        json_data = json.loads(data)

        if json_data["nsfw"]:
            await ctx.send(content=_("errors.nsfw", ctx), ephemeral=True)
            return

        embed = create_embed(
            title_url=json_data["postLink"],
            title=json_data["title"],
            image=json_data["url"],
            author_text=f"r/{json_data['subreddit']} | u/{json_data['author']}",
            author_image=get_emote("reddit", return_type="image"),
        )
        await ctx.send(embed=embed)

    @commands.slash_command(name="gigachadify")
    async def gigachadify_slash(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        user: Optional[disnake.Member] = None,
    ) -> None:
        """
        ✨ Turn you or someone else into a Giga Chad!

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        user : disnake.Member, optional
            The user to gigachadify
        """
        await gigachadify(ctx, user)

    @commands.user_command(name="Gigachadify")
    async def gigachadify_user(
        self, ctx: disnake.ApplicationCommandInteraction, user: Optional[disnake.Member]
    ) -> None:
        """
        ✨ Turn you or someone else into a Giga Chad!

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        user : disnake.Member, optional
            The user to gigachadify
        """
        await gigachadify(ctx, user)

    @commands.slash_command(name="chadmeter")
    async def chadmeter_slash(
        self, ctx: disnake.ApplicationCommandInteraction, user: Optional[disnake.Member] = None
    ) -> None:
        """
         📏 Scientifically measure your Chad level

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        user : disnake.member, optional
            The user to measure
        """
        await chadmeter(ctx, user)

    @commands.user_command(name="Chadmeter")
    async def chadmeter_user(
        self, ctx: disnake.ApplicationCommandInteraction, user: Optional[disnake.Member]
    ) -> None:
        """
         📏 Scientifically measure your Chad level

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        user : disnake.member, optional
            The user to measure
        """
        await chadmeter(ctx, user)

    @commands.slash_command(name="caption")
    async def caption(
        self,
        ctx: disnake.ApplicationCommandInteraction,
        top_caption: str,
        bottom_caption: str,
        template: str = commands.Param(choices=caption_templates),
    ) -> None:
        """
        🎭 Create a meme, many  meme templates available!

        Parameters
        ----------
        ctx : disnake.ApplicationCommandInteraction
            The context of the command
        top_caption : str
            The top caption
        bottom_caption : str
            Write the bottom text
        template : str
            Choose a meme template
        """
        pload = {
            "font": "impact",
            "username": IMGFLIP_USERNAME,
            "password": IMGFLIP_PASSWORD,
            "template_id": template,
            "text1": bottom_caption,
            "text0": top_caption,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.imgflip.com/caption_image", data=pload
            ) as r:
                data = await r.read()

        if r.status != 200:
            await error_api(ctx)
            return

        json_data = json.loads(data)
        embed = create_embed(
            image=json_data["data"]["url"],
            author_url=json_data["data"]["page_url"],
            author_text=_("fun.caption.click", ctx),
            footer_text=_("fun.caption.footer", ctx),
        )
        await ctx.send(embed=embed)


async def chadmeter(
    ctx: disnake.ApplicationCommandInteraction, user: Optional[disnake.Member]
) -> None:
    if user is None:  # check if a user param is specified

        if await has_voted(ctx.author.id):  # check if this user has voted on top.gg
            chadlevel = random.randint(
                75, 100
            )  # give a higher chadlevel if it is the case
            footer_icon = ctx.bot.user.avatar_url
            footer_text = _("fun.chadmeter.footer.voted", ctx)

        else:
            chadlevel = random.randint(-1, 90)  # lower given chadlevel elsewhere
            footer_icon = get_emote("hint", return_type="image")
            footer_text = _(
                "fun.chadmeter.footer.notvoted",
                ctx
            )
            # user is told that voting for the bot inscreases chadlever

        desc = _("fun.chadmeter.desc.own", ctx, chadlevel=chadlevel)

    else:
        if await has_voted(user.id):  # same as above
            chadlevel = random.randint(80, 100)

        elif user == ctx.bot.user:  # if user param is bot:
            chadlevel = 100

        else:
            chadlevel = random.randint(-1, 80)

        footer_icon = ctx.bot.user.display_avatar.url
        footer_text = _("fun.chadmeter.footer.voted", ctx)
        desc = _(
            "fun.chadmeter.desc.other", ctx, user=user.mention, chadlevel=chadlevel
        )

    # creates progress bar
    grey = get_emote("ChadmeterGrey")
    blurple = get_emote("ChadmeterBlurple")
    rn = round(chadlevel / 10)
    body = "░" * 10
    li = list(body)
    for i, elem in enumerate(li[:rn]):
        li[i] = "▓"
    a = "".join(li)
    b = a.replace("▓", blurple)
    c = b.replace("░", grey)
    d = f"{desc}\n\n{get_emote('ChadmeterStart')}{c}{get_emote('ChadmeterEnd')}\n{get_emote('blank')}"

    embed = create_embed(
        title=_("fun.chadmeter.title", ctx),
        desc=d,
        footer_icon=footer_icon,
        footer_text=footer_text,
        thumbnail="https://preview.redd.it/23td86ox29j51.png?auto=webp&s=c617e39e98b1e601cc91168369bd6ea38cd55f89",
    )

    await ctx.send(embed=embed)


async def gigachadify(
    ctx: disnake.ApplicationCommandInteraction, user: Optional[disnake.Member] = None
) -> None:
    """
    🎭 GigaChadify a user!

    Parameters
    ----------
    ctx : disnake.ApplicationCommandInteraction
        The context of the command
    user : Optional[disnake.Member]
        The user to gigachadify
    """
    if user is None:
        asset = ctx.author.display_avatar.replace(size=128)
        prefix = _("fun.gigachadify.title.own", ctx)

        data = BytesIO(await asset.read())  # Load the user's profile picture

        # run sync code asyncronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, gigachadify_process, data)

        file = disnake.File("output.jpg")
        attachment = "attachment://output.jpg"

    elif user == ctx.bot.user:
        prefix = _("fun.gigachadify.title.giga_chad", ctx)
        file = disnake.File("ressources/gigachad.png")
        attachment = "attachment://gigachad.png"

    else:
        asset = user.display_avatar.replace(size=128, static_format="jpg")
        prefix = _("fun.gigachadify.title.other", ctx, user=user.name)

        data = BytesIO(await asset.read())  # Load the user's profile picture

        # run sync code asyncronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, gigachadify_process, data)

        file = disnake.File("output.jpg")
        attachment = "attachment://output.jpg"

    embed = create_embed(
        title=prefix,
        footer_icon=ctx.bot.user.display_avatar.url,
        footer_text=_("fun.gigachadify.footer", ctx),
        image=attachment,
    )

    await ctx.send(file=file, embed=embed)


def gigachadify_process(data) -> None:
    im2 = Image.open(data)  # open the image
    im2 = im2.resize((175, 175))  # Resize it
    im2 = im2.rotate(7)  # Slightly rotate the profile picture

    mask_im = Image.new("L", im2.size, 0)  # Create a new "mask"
    draw = ImageDraw.Draw(mask_im)  #
    draw.ellipse([(0, 0), (175, 175)], fill=255)  # Draw an ellipse on it
    mask_im.save("mask_circle.jpg", quality=95)  # Save the mask

    im1 = Image.open("ressources/gigachad.png")  # Open Giga Chad imahe
    im1.paste(
        im2, (300, 85), mask_im
    )  # Paste the profile picture on Giga Chad with the mask
    im1.save("output.jpg", quality=95)  # Save it for upload


async def error_api(ctx: disnake.ApplicationCommandInteraction) -> None:
    """
    Create an embed if api can't be reached or in case of any error

    Parameters
    ----------
    ctx : disnake.ApplicationCommandInteraction
        The context where the command was called
    """
    embed = create_embed(
        title=_("errors.api.title", ctx, emote=get_emote("warning")),
        desc=_("errors.api.desc", ctx),
    )
    await ctx.send(embed=embed, ephemeral=True)


def setup(bot: commands.AutoShardedBot) -> None:
    bot.add_cog(Fun(bot))
