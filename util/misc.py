import json
import os
import disnake
import i18n
import aiohttp
from typing import Optional, List, Tuple, Union
from disnake.ext import tasks, commands

i18n.set("skip_locale_root_data", True)
i18n.translations.container.clear()  # invalidate old cache
i18n.set("file_format", "yaml")
i18n.set("filename_format", "{locale}.{format}")
i18n.set("fallback", "en")
i18n.load_path.append("./ressources/locales/")

beta = os.getenv("BETA") == "TRUE"

path = "ressources/beta-emotes.json" if beta else "ressources/emotes.json"
with open(path, "r") as f:
    emotes = json.load(f)

with open("ressources/locales/supported-locales.json", "r") as f:
    supported_locales = json.load(f)


def get_lang(bot: commands.AutoShardedBot, ctx: disnake.ApplicationCommandInteraction) -> str:
    """
    Returns a server/user language from a given context

    Parameters
    ----------
    bot : commands.AutoShardedBot
        The bot instance
    ctx : disnake.ApplicationCommandInteraction,
        The context to get the language from

    Returns
    -------
    str
        The language for the given context
    """
    if ctx.guild_locale is not None and "COMMUNITY" in ctx.guild.features:
        locale = ctx.guild_locale
    else:
        locale = ctx.locale

    return next(
        (supported_locales[lang] for lang in supported_locales.keys() if locale.startswith(lang)), "en"
    )


def translate(key: str, ctx: disnake.ApplicationCommandInteraction, **kwargs) -> str:
    """
    Return a translated string from locales

    Parameters
    ----------
    key : str
        The key to translate
    ctx : disnake.ApplicationCommandInteraction
        The context to get the language from
    kwargs : dict
        The arguments to pass to the string

    Returns
    -------
    str
        The translated string
    """
    lang = get_lang(ctx.bot, ctx)
    return i18n.t(key, locale=lang, **kwargs)


def get_emote(emote: str, return_type: Optional[str] = None) -> Union[str, int]:
    """
    Return an emote from  the `emotes.json` or `beta-emotes.json` file

    Parameters
    ----------
    emote : str
        Name of the emote to get
    return_type : Optional[str], optional
        Type of the emote to get, by default the full emote, can be `id` or `image`

    Returns
    -------
    Union[str, int]
        The returned emote, is a string if type is `id`, and a link,
        if type is `image`, if type is None, the full emote code is returned
    """
    if str(emote) not in emotes:
        return ":exclamation:"

    if return_type is None:
        return emotes[str(emote)]

    elif return_type == "id":
        return int(emotes[str(emote)].split(":")[2][:-1])

    elif return_type == "image":
        return f"https://cdn.discordapp.com/emojis/{emotes[str(emote)].split(':')[2][:-1]}.png"


async def has_voted(user_id: int) -> bool:
    """
    Checks from the top.gg API if a user has voted

    Parameters
    ----------
    user_id : int
        The user id to check

    Returns
    -------
    bool
        True if the user has voted, False otherwise, always False if beta is True
    """
    if not beta:
        url = f"https://top.gg/api/bots/843550872293867570/check?userId={user_id}"
        headers = {"Authorization": os.getenv("TOPGG_TOKEN")}

        async with aiohttp.ClientSession() as c:
            async with c.get(url, headers=headers) as r:
                dat = await r.read()

        if r.status != 200:
            return False

        json_data = json.loads(dat)
        if json_data["voted"] == 1:
            return True

    return False


def create_embed(
        title: Optional[str] = None,
        desc: Optional[str] = None,
        fields: Optional[List[Tuple[str, str, Optional[bool]]]] = None,
        color: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None,
        footer_text: Optional[str] = None,
        footer_icon: Optional[str] = None,
        author_text: Optional[str] = None,
        author_image: Optional[str] = None,
        author_url: Optional[str] = None,
        title_url: Optional[str] = None,
) -> disnake.Embed:
    """
    Create an embed easily

    Parameters
    ----------
    title : Optional[str], optional
        The title of the embed
    desc : Optional[str], optional
        The description of the embed
    fields : Optional[List[Tuple[str, str, Optional[bool]]]], optional
        List of fields, each field is a tuple of (name, value, inline)
    color : Optional[str], optional
        The color of the embed
    image : Optional[str], optional
        The image of the embed
    thumbnail : Optional[str], optional
        The thumbnail of the embed
    footer_text : Optional[str], optional
        The text of the footer
    footer_icon : Optional[str], optional
        The icon of the footer
    author_text : Optional[str], optional
        The text of the author
    author_image : Optional[str], optional
        The image of the author
    author_url : Optional[str], optional
        The url of the author
    title_url : Optional[str], optional
        The url of the title

    Returns
    -------
    disnake.Embed
        The created embed
    """

    if color is None:
        color = 0x2F3136

    elif color == "green":
        color = 0x57F287

    elif color == "red":
        color = 0xED4245

    if desc is None:
        if title_url is None:
            if title is None:
                embed = disnake.Embed(color=color)

            else:
                embed = disnake.Embed(title=title, color=color)

        else:
            embed = disnake.Embed(title=title, color=color, url=title_url)

    elif title_url is None:
        if title is None:
            embed = disnake.Embed(description=desc, color=color)

        else:
            embed = disnake.Embed(title=title, description=desc, color=color)

    else:
        embed = disnake.Embed(title=title, description=desc, color=color, url=title_url)

    if fields is not None:

        for x in range(len(fields)):
            inline = True in fields[x]
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
                embed.set_author(
                    name=author_text, url=author_url, icon_url=author_image
                )

            else:
                embed.set_author(name=author_text, icon_url=author_image)

        elif author_url is not None:
            embed.set_author(name=author_text, url=author_url)

        else:
            embed.set_author(name=author_text)

    return embed
