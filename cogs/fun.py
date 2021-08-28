import random
import discord
import urllib.request
import aiohttp
import os
import json
import asyncio

from PIL import Image, ImageDraw
from io import BytesIO
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.context import MenuContext
from discord_slash.model import ContextMenuType
from discord_slash.utils.manage_commands import create_option, create_choice

from cogs.prefix import get_prefix
from cogs.logging import log_cmd
from util.misc import get_emote, create_embed, has_voted
from util.misc import translate as _

IMGFLIP_USERNAME = os.getenv("IMGFLIP_USERNAME")  # These env variables are called here
IMGFLIP_PASSWORD = os.getenv("IMGFLIP_PASSWORD")  # to have them loaded only once at runtime


# Retrieve the GigaChad image for gigachadify cmd


class Fun(commands.Cog):
    """
    Fun stuff goes here!
    (!) Slash cmds and normal cmds call outside functions
    to make them compatible with both uses (!)
    """

    def __init__(self, gigachad):
        self.gigachad = gigachad

    # MEME
    @cog_ext.cog_slash(name="Meme", description='🎲 Get a random meme!',
                       options=[
                           create_option(
                               name="subreddit",
                               description="Get a meme from a particular subreddit",
                               option_type=3,
                               required=False,
                           )])
    async def slashmeme(self, ctx: SlashContext, subreddit=None):
        await meme(ctx, subreddit, True)

    @commands.command(name="meme", usage="meme [subreddit]",
                      description="Get a random meme from reddit or from a specific subreddit! Just type the name of "
                                  "the subreddit, like 'fun' instead of 'r/fun' !")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdmeme(self, ctx, subreddit: str = None):
        await meme(ctx, subreddit)

    # GIGACHADIFY
    @cog_ext.cog_context_menu(name="Gigachadify",
                              target=ContextMenuType.USER)
    async def menugigachadify(self, ctx: MenuContext):
        if ctx.author == ctx.target_author:
            user = None
        else:
            user = ctx.target_author
        await gigachadify(ctx=ctx, bot=self.gigachad, user=user, slash=True)
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
    async def slashgigachadify(self, ctx: SlashContext, user: discord.user = None):
        await gigachadify(ctx, self.gigachad, user, True)

    @commands.command(
        name="gigachadify",
        usage="gigachadify [user]",
        description="Turn you or someone else into a Giga Chad!"
    )
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def cmdgigachadify(self, ctx, user: commands.MemberConverter = None):
        await gigachadify(ctx, self.gigachad, user)

    # CHADMETER
    @cog_ext.cog_context_menu(name="Chadmeter",
                              target=ContextMenuType.USER)
    async def chadmetermenu(self, ctx: MenuContext):
        if ctx.author == ctx.target_author:
            user = None
        else:
            user = ctx.target_author
        await chadmeter(ctx=ctx, bot=self.gigachad, user=user, slash=True)
        await log_cmd(self.gigachad, ctx, ctx, 3)

    @cog_ext.cog_slash(name="chadmeter", description="📏 Scientifically measure your Chad level",
                       options=[
                           create_option(
                               name="user",
                               description="Check the chad lever of another user",
                               option_type=6,
                               required=False,
                           )])
    async def slashchadmeter(self, ctx: SlashContext, user: discord.user = None):
        await chadmeter(ctx, self.gigachad, user, True)

    @commands.command(name="chadmeter", usage="chadmeter [user]",
                      description="Scientifcally measure your or someone else's Chad level!")
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdchadmeter(self, ctx, user: commands.MemberConverter = None):
        await chadmeter(ctx, self.gigachad, user)

    # CAPTION
    @cog_ext.cog_slash(name="caption",
                       description="🎭 Caption a meme, 25 meme templates available!",
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
    async def caption(self, ctx: SlashContext, template: int, top_caption: str, bottom_caption: str):
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
            await ctx.send(embed=embed, hidden=False)

        except:
            await error_api(ctx)

    @cog_ext.cog_slash(
        name="quote",
        description="💬 Get an inspiring quote to get closer to being a Giga Chad"
    )
    async def slashquote(self, ctx: SlashContext):
        await quote(ctx, True)

    @commands.command(
        name="quote",
        usage="quote",
        description="Get an inspiring quote to get closer to being a Giga Chad"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdquote(self, ctx):
        await quote(ctx)

    @cog_ext.cog_slash(
        name="advice",
        description="💡 Get some advice from Giga Chad"
    )
    async def slashadvice(self, ctx: SlashContext):
        await advice(ctx, True)

    @commands.command(
        name="advice",
        usage="advice",
        description="Get some advice from Giga Chad!"
    )
    @commands.cooldown(1, 3, commands.BucketType.user)
    async def cmdadvice(self, ctx):
        await advice(ctx)


async def meme(ctx, subreddit: str = None, slash: bool = False):
    try:
        if subreddit is None:
            json_data = await fetch('https://meme-api.herokuapp.com/gimme')

        else:
            json_data = await fetch(f'https://meme-api.herokuapp.com/gimme/{subreddit}')

        nsfw = json_data['nsfw']

        if nsfw:

            if slash:
                await ctx.send(content=_("errors.nsfw", ctx), hidden=True)

            else:
                await ctx.reply(
                    content=_("errors.nsfw", ctx), mention_author=False)

            return

        embed = create_embed(
            title_url=json_data['postLink'],
            title=json_data['title'],
            footer_text=f"r/{json_data['subreddit']} | u/{json_data['author']}",
            footer_icon="https://cdn.discordapp.com/emojis/879795881036099584.png?v=1",
            image=json_data['url']
        )

        if slash:
            await ctx.send(embed=embed)

        else:
            await ctx.reply(embed=embed, mention_author=False)

    except:
        await error_api(ctx, slash)


async def advice(ctx, slash: bool = False):
    try:
        json_data = await fetch('https://api.adviceslip.com/advice')
        advice_slip = json_data['slip']['advice']
        embed = create_embed(
            title=_("fun.advice.title", ctx),
            description=f"🗣 {advice_slip}",
            footer_text=_("fun.advice.footer", ctx)
        )

        if slash:
            await ctx.send(embed=embed, hidden=False)

        else:
            await ctx.reply(embed=embed, mention_author=False)

    except:
        await error_api(ctx, slash)


async def chadmeter(ctx, bot, user, slash: bool = False):
    if user is None:
        if await has_voted(ctx.author.id):
            chadlevel = random.randint(80, 100)
            footer_icon = bot.user.avatar_url
            footer_text = _("fun.chadmeter.footer.voted", ctx)

        else:
            chadlevel = random.randint(-1, 80)
            footer_icon = "https://cdn.discordapp.com/emojis/879697097467789373.png?v=1"
            footer_text = _("fun.chadmeter.footer.notvoted", ctx, prefix=get_prefix(bot, ctx, raw=True))

        desc = _("fun.chadmeter.desc.own", ctx, chadlevel=chadlevel)

    else:
        if await has_voted(user.id):
            chadlevel = random.randint(80, 100)

        elif user == bot.user:
            chadlevel = 100

        else:
            chadlevel = random.randint(-1, 80)

        footer_icon = bot.user.avatar_url
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
        await ctx.reply(embed=embed, mention_author=False)


async def quote(ctx, slash: bool = False):
    try:
        json_data = await fetch("https://api.quotable.io/random")
        quote_slip = json_data['content']
        author = json_data['author']
        embed = create_embed(
            title=_("fun.quote.title", ctx),
            description=f"{get_emote('quote1')} \n**{quote_slip}* \n \n - {author} {get_emote('quote2')}",
            footer_text=_("fun.quote.footer", ctx)
        )

        if slash:
            await ctx.send(embed=embed, hidden=False)

        else:
            await ctx.reply(embed=embed, mention_author=False)

    except:
        await error_api(ctx, slash)


async def gigachadify(ctx, bot: discord.client, user=None, slash: bool = False):
    if user is None:
        asset = ctx.author.avatar_url_as(size=128)
        prefix = _("fun.gigachadify.title.own", ctx)

    else:
        asset = user.avatar_url_as(size=128)
        prefix = _("fun.gigachadify.title.other", ctx, user=user.name)
    data = BytesIO(await asset.read())  # Load the user's profile picture

    # run sync code asyncronously
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, gigachadify_process, data)

    file = discord.File("test.jpg")
    attachment = "attachment://test.jpg"

    if user is not None:

        if user.id == bot.user.id:
            prefix = _("fun.gigachadify.title.giga_chad", ctx)
            file = discord.File("gigachad.png")
            attachment = "attachment://gigachad.png"

    embed = create_embed(
        title=prefix,
        footer_icon=bot.user.avatar_url,
        footer_text=_("fun.gigachadify.footer", ctx),
        image=attachment
    )

    if slash:
        await ctx.send(file=file, embed=embed)

    else:
        await ctx.reply(file=file, embed=embed, mention_author=False)


def gigachadify_process(data):
    im2 = Image.open(data)  #
    im2 = im2.resize((175, 175))  # Resize it
    im2 = im2.rotate(7)  # Slightly rotate the profile picture

    mask_im = Image.new("L", im2.size, 0)  # Create a new "mask"
    draw = ImageDraw.Draw(mask_im)  #
    draw.ellipse([(0, 0), (175, 175)], fill=255)  # Draw an ellipse on it
    mask_im.save('mask_circle.jpg', quality=95)  # Save the mask

    im1 = Image.open("ressources/gigachad.png")  # Open Giga Chad imahe
    im1.paste(im2, (300, 85), mask_im)  # Paste the profile picture on Giga Chad with the mask
    im1.save("test.jpg", quality=95)  # Save it for upload


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as r:
            data = await r.read()

    return json.loads(data)


async def error_api(ctx, slash: bool = False):
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
