from typing import Union, Optional
import json
import os
import random
import asyncio
from io import BytesIO
import aiohttp
import discord
from PIL import Image, ImageDraw
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType, ButtonStyle
from discord_slash.utils.manage_commands import create_option, create_choice
from discord_slash.utils.manage_components import create_button, create_actionrow

from cogs.logging import log_cmd
from cogs.prefix import get_prefix
from util.misc import get_emote, create_embed, has_voted
from util.misc import translate as _

IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")  # load env variables
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")

eol_txt_cmds = create_embed(
    author_text="Text Commands Soon Unsupported",
    author_image=get_emote("hint", type="image"),
    desc=f"{get_emote('dot')} Text commands will soon be unsupported by Giga Chad due to descisions Discord is "
         f"taking. Read more about it [here](https://support-dev.discord.com/hc/en-us/articles/4404772028055-Message"
         f"-Content-Access-Deprecation-for-Verified-Bots). [tldr; Giga Chad won't have access to message contents].\n"
         f"{get_emote('dot')}Start switching to [Slash Commands now!",
    color="red"
)


class Fun(commands.Cog):
    """
    Fun stuff goes here!
    Slash cmds, context menus and normal cmds call outside functions
    to make them compatible with all these uses 
    """

    def __init__(self, gigachad: commands.Bot) -> None:
        self.gigachad = gigachad

    # MEMES commands
    @cog_ext.cog_slash(name="Meme", description='🎲 Get a random meme!',
                       options=[
                           create_option(
                               name="subreddit",
                               description="Get a meme from a particular subreddit",
                               option_type=3,
                               required=False,
                           )])
    async def slashmeme(self, ctx: SlashContext, subreddit: Optional[str] = None) -> None:
        await meme(ctx, subreddit, True)

    @commands.command(name="meme", usage="meme [subreddit]",
                      description="Get a random meme from reddit or from a specific subreddit! Just type the name of "
                                  "the subreddit, like 'fun' instead of 'r/fun' !")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdmeme(self, ctx: commands.Context, subreddit: Optional[str] = None):
        await meme(ctx, subreddit)

    # GIGACHADIFY commands
    @cog_ext.cog_context_menu(name="Gigachadify", target=ContextMenuType.USER)
    async def menugigachadify(self, ctx: MenuContext) -> None:
        if ctx.author == ctx.target_author:
            user = None
        else:
            user = ctx.target_author
        await gigachadify(ctx=ctx, user=user, slash=True)
        await log_cmd(self.gigachad, ctx, ctx, 3)

    @cog_ext.cog_slash(
        name="gigachadify",
        description="💫 Gigadify yourself or another user!",
        options=[
            create_option(
                name="user",
                description="GigaChadify another user!",
                option_type=6,
                required=False,
            )
        ]
    )
    async def slashgigachadify(self, ctx: SlashContext, user: Optional[discord.Member] = None) -> None:
        await gigachadify(ctx, user, True)

    @commands.command(
        name="gigachadify",
        usage="gigachadify [user]",
        description="Turn you or someone else into a Giga Chad!"
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cmdgigachadify(self, ctx: commands.context, user: Optional[commands.MemberConverter] = None) -> None:
        await gigachadify(ctx, user)

    # CHADMETER commands
    @cog_ext.cog_context_menu(name="Chadmeter", target=ContextMenuType.USER)
    async def chadmetermenu(self, ctx: MenuContext) -> None:
        if ctx.author == ctx.target_author:
            user = None

        else:
            user = ctx.target_author

        await chadmeter(ctx=ctx, user=user, slash=True)
        await log_cmd(self.gigachad, ctx, ctx, 3)

    @cog_ext.cog_slash(name="chadmeter", description="📏 Scientifically measure your Chad level",
                       options=[
                           create_option(
                               name="user",
                               description="Check the chad lever of another user",
                               option_type=6,
                               required=False,
                           )])
    async def slashchadmeter(self, ctx: SlashContext, user: Optional[discord.Member] = None):
        await chadmeter(ctx, user, True)

    @commands.command(name="chadmeter", usage="chadmeter [user]",
                      description="Scientifcally measure your or someone else's Chad level!")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdchadmeter(self, ctx: commands.context, user: Optional[commands.MemberConverter] = None) -> None:
        await chadmeter(ctx, self.gigachad, user)

    # CAPTION
    @cog_ext.cog_slash(name="caption",
                       description="🎭 Create a meme, 25 meme templates available!",
                       options=[
                           create_option(
                               name="template",
                               description="Choose a meme template",
                               option_type=3,
                               required=True,
                               choices=[
                                   create_choice(name="Two Buttons", value="87743020"),
                                   create_choice(name="Distracted Boyfriend", value="112126428"),
                                   create_choice(name="Drake Yikes", value="181913649"),
                                   create_choice(name="Batman Slaps Robin", value="438680"),
                                   create_choice(name="Trade Offer", value="309868304"),
                                   create_choice(name="Change my Mind", value="129242436"),
                                   create_choice(name="UNO Draw 25", value="217743513"),
                                   create_choice(name="Woman Yelling at Cat", value="188390779"),
                                   create_choice(name="Inhaling Seagull", value="114585149"),
                                   create_choice(name="Giga Chad", value="190327839"),
                                   create_choice(name="Another Woman", value="110163934"),
                                   create_choice(name="Same Pictures", value="180190441"),
                               ]
                           ),
                           create_option(
                               name="top_caption",
                               description="Write the top text",
                               option_type=3,
                               required=True
                           ),
                           create_option(
                               name="bottom_caption",
                               description="Write the bottom text",
                               option_type=3,
                               required=True
                           ),
                       ])
    async def make_meme(self, ctx: SlashContext, template: int, top_caption: str, bottom_caption: str) -> None:
        try:
            pload = {'font': 'impact', 'username': IMGFLIP_USERNAME, 'password': IMGFLIP_PASSWORD,
                     'template_id': template, 'text1': bottom_caption, 'text0': top_caption}
            async with aiohttp.ClientSession() as session:
                async with session.post('https://api.imgflip.com/caption_image', data=pload) as r:
                    data = await r.read()
            json_data = json.loads(data)
            embed = create_embed(
                image=json_data['data']['url'],
                author_url=json_data['data']['page_url'],
                author_text=_("fun.caption.click", ctx),
                footer_text=_("fun.caption.footer", ctx)
            )
            buttons = [
                create_button(
                    style=ButtonStyle.grey,
                    label="Save to gallery",
                    custom_id=f"save_{ctx.author.id}",
                    emoji=ctx.bot.get_emoji(get_emote("add", type='id'))
                )
            ]
            await ctx.send(embed=embed, components=[create_actionrow(*buttons)], hidden=False)

        except:
            await error_api(ctx)


async def meme(ctx: Union[SlashContext, commands.Context], subreddit: Optional[str] = None,
               slash: Optional[bool] = False) -> None:
    try:
        # first fetch the meme from an api
        if subreddit is None:
            json_data = await fetch('https://meme-api.herokuapp.com/gimme')

        else:
            json_data = await fetch(f'https://meme-api.herokuapp.com/gimme/{subreddit}')

        nsfw = json_data['nsfw']

        if nsfw:  # no nsfw memes shall be sent, even in nsfw channels

            if slash:
                await ctx.send(content=_("errors.nsfw", ctx), hidden=True)

            else:
                await ctx.reply(
                    content=_("errors.nsfw", ctx), mention_author=False)

            return

        embed = create_embed(
            title_url=json_data['postLink'],
            title=json_data['title'],
            image=json_data['url'],
            author_text=f"r/{json_data['subreddit']} | u/{json_data['author']}",
            author_image=get_emote('reddit', type='image')
        )
        buttons = [
            create_button(
                style=ButtonStyle.grey,
                label="Save to gallery",
                custom_id=f"save_{ctx.author.id}",
                emoji=ctx.bot.get_emoji(get_emote("add", type='id'))
            )
        ]
        if slash:
            await ctx.send(embed=embed, components=[create_actionrow(*buttons)])

        else:
            await ctx.reply(embed=eol_txt_cmds, mention_author=False,)
            await ctx.send(embed=embed, components=[create_actionrow(*buttons)])


    except:
        await error_api(ctx, slash)


async def chadmeter(ctx: Union[SlashContext, commands.Context, MenuContext], user: Optional[discord.Member],
                    slash: Optional[bool] = False) -> None:
    if user is None:  # check if a user param is specified

        if await has_voted(ctx.author.id):  # check if this user has voted on top.gg
            chadlevel = random.randint(75, 100)  # give a higher chadlevel if it is the case
            footer_icon = ctx.bot.user.avatar_url
            footer_text = _("fun.chadmeter.footer.voted", ctx)

        else:
            chadlevel = random.randint(-1, 90)  # lower given chadlevel elsewhere
            footer_icon = get_emote('hint', type='image')
            footer_text = _("fun.chadmeter.footer.notvoted", ctx, prefix=get_prefix(ctx.bot, ctx, raw=True))
            # user is told that voting for the bot inscreases chadlever

        desc = _("fun.chadmeter.desc.own", ctx, chadlevel=chadlevel)

    else:
        if await has_voted(user.id):  # same as above
            chadlevel = random.randint(80, 100)

        elif user == ctx.bot.user:  # if user param is bot:
            chadlevel = 100

        else:
            chadlevel = random.randint(-1, 80)

        footer_icon = ctx.bot.user.avatar_url
        footer_text = _("fun.chadmeter.footer.voted", ctx)
        desc = _("fun.chadmeter.desc.other", ctx, user=user.mention, chadlevel=chadlevel)

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
        thumbnail="https://preview.redd.it/23td86ox29j51.png?auto=webp&s=c617e39e98b1e601cc91168369bd6ea38cd55f89"
    )

    if slash:
        await ctx.send(embed=embed, hidden=False)

    else:
        await ctx.reply(embed=eol_txt_cmds, mention_author=False)
        await ctx.send(embed=embed)


async def gigachadify(ctx: Union[SlashContext, commands.Context, MenuContext], user: Optional[discord.Member] = None,
                      slash: Optional[bool] = False) -> None:
    if user is None:
        asset = ctx.author.avatar_url_as(size=128)
        prefix = _("fun.gigachadify.title.own", ctx)

        data = BytesIO(await asset.read())  # Load the user's profile picture

        # run sync code asyncronously
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, gigachadify_process, data)

        file = discord.File("output.jpg")
        attachment = "attachment://output.jpg"

    else:

        if user == ctx.bot.user:
            prefix = _("fun.gigachadify.title.giga_chad", ctx)
            file = discord.File("ressources/gigachad.png")
            attachment = "attachment://gigachad.png"

        else:
            asset = user.avatar_url_as(size=128)
            prefix = _("fun.gigachadify.title.other", ctx, user=user.name)

            data = BytesIO(await asset.read())  # Load the user's profile picture

            # run sync code asyncronously
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(None, gigachadify_process, data)

            file = discord.File("output.jpg")
            attachment = "attachment://output.jpg"

    embed = create_embed(
        title=prefix,
        footer_icon=ctx.bot.user.avatar_url,
        footer_text=_("fun.gigachadify.footer", ctx),
        image=attachment
    )

    if slash:
        await ctx.send(file=file, embed=embed)

    else:
        await ctx.reply(embed=eol_txt_cmds, mention_author=False)
        await ctx.send(file=file, embed=embed)


def gigachadify_process(data) -> None:
    im2 = Image.open(data)  # open the image
    im2 = im2.resize((175, 175))  # Resize it
    im2 = im2.rotate(7)  # Slightly rotate the profile picture

    mask_im = Image.new("L", im2.size, 0)  # Create a new "mask"
    draw = ImageDraw.Draw(mask_im)  #
    draw.ellipse([(0, 0), (175, 175)], fill=255)  # Draw an ellipse on it
    mask_im.save('mask_circle.jpg', quality=95)  # Save the mask

    im1 = Image.open("ressources/gigachad.png")  # Open Giga Chad imahe
    im1.paste(im2, (300, 85), mask_im)  # Paste the profile picture on Giga Chad with the mask
    im1.save("output.jpg", quality=95)  # Save it for upload


async def fetch(url: str) -> dict:
    """ Method to easily fetech data from an api """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.read()

    return json.loads(data)


async def error_api(ctx: Union[commands.Context, SlashContext, MenuContext], slash: Optional[bool] = False) -> None:
    """ Create an embed if api can't be reached
    or in cas of any error """
    embed = create_embed(
        title=_("errors.api.title", ctx, emote=get_emote("warning")),
        desc=_("errors.api.desc", ctx)
    )

    if slash:
        await ctx.send(embed=embed, hidden=True)

    else:
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
