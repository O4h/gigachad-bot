import json
import os
import discord
import i18n
import aiohttp
from discord.ext import tasks, commands
from cogs.lang import get_lang

i18n.set('skip_locale_root_data', True)
i18n.translations.container.clear()  # invalidate old cache
i18n.set('file_format', 'yaml')
i18n.set('filename_format', '{locale}.{format}')
i18n.set('fallback', 'en')
i18n.load_path.append('./ressources/locales/')


def translate(key: str, ctx, **kwargs) -> str:
    """ Return a translated string from locales"""
    lang = get_lang(ctx.bot, ctx)
    return i18n.t(key, locale=lang, **kwargs)
            
            
def get_emote(emote: str) -> str:
    """ Return an emote from emotes.json"""
    with open('ressources/emotes.json', 'r') as f:
        emotes = json.load(f)

    if str(emote) in emotes:
        return emotes[str(emote)]

    else:
        return ":exclamation:"


async def has_voted(user_id: int) -> bool:
    url = f"https://top.gg/api/bots/843550872293867570/check?userId={user_id}"
    headers = {"Authorization": os.getenv("TOPGG_TOKEN")}
    async with aiohttp.ClientSession() as c:
        async with c.get(url, headers=headers) as r:
            dat = await r.read()
    json_data = json.loads(dat)
    if json_data["voted"] == 1:
        return True
    else:
        return False


def create_embed(title: str = None, desc: str = None, fields: list = None, color=None,
                 image: str = None, thumbnail: str = None, footer_text: str = None, footer_icon: str = None,
                 author_text: str = None, author_image: str = None, author_url: str = None,
                 title_url: str = None) -> discord.Embed:
    """
    Create an embed easily
    Either :param title: or :param desc:
    is required to get it working
    """

    if color is not None:

        if color == "green":
            color = 0x57f287

        elif color == "red":
            color = 0xed4245

    else:
        color = 0x2f3136

    if title is None:
        embed = discord.Embed(description=desc, color=color)

    else:

        if desc is None:
            if title_url is None:
                embed = discord.Embed(title=title, color=color)

            else:
                embed = discord.Embed(title=title, color=color, url=title_url)

        else:
            if title_url is None:
                embed = discord.Embed(title=title, description=desc, color=color)

            else:
                embed = discord.Embed(title=title, description=desc, color=color, url=title_url)

    if fields is not None:

        for x in range(len(fields)):
            if True in fields[x]:
                inline = True

            else:
                inline = False

            embed.add_field(name=fields[x][0], value=fields[x][1], inline=inline)

    if thumbnail is not None:
        embed.set_thumbnail(url=thumbnail)

    if image is not None:
        embed.set_image(url=image)

    if footer_text is not None:
        if footer_icon is not None:
            embed.set_footer(text=footer_text, icon_url=footer_icon)

        else:
            embed.set_footer(text=footer_text)

    if author_text is not None:
        if author_image is not None:
            if author_url is not None:
                embed.set_author(name=author_text, url=author_url, icon_url=author_image)

            else:
                embed.set_author(name=author_text, icon_url=author_image)

        else:
            if author_url is not None:
                embed.set_author(name=author_text, url=author_url)

            else:
                embed.set_author(name=author_text)

    return embed
