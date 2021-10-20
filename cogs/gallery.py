import asyncio
import json
import os
import random
import string
import time
from datetime import datetime

import aiohttp
import discord
import discord_slash
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.context import InteractionContext, ComponentContext
from discord_slash.model import ButtonStyle
from discord_slash.utils.manage_commands import create_option
from discord_slash.utils.manage_components import *
from util.misc import create_embed, get_emote
from util.misc import translate as _

imgur_id = os.getenv("IMGUR_ID")


async def generate_key(bot: commands.Bot) -> str:
    """ Generates a unique key to map to a saved image
    :param bot: the bot, used to acquire the db connection
    """
    different = False  # Whether the key is unique

    while different is False:
        key = ''.join(random.choices(string.ascii_letters, k=5)).upper()

        async with bot.db.acquire() as conn:
            count = dict(await conn.fetchrow("SELECT COUNT(*) FROM gallery WHERE id = $1", key))

        if count['count'] == 0:
            different = True

    return key


async def send_meme(ctx: commands.Context, data: dict, hidden: bool = False) -> None:
    """ Send a meme to discord
    :param ctx: the context to where the meme is going to be sent
    :param data: contains the data returned from the db as dict
    :param hidden: whether the embed should be sent in response or not
    """
    embed = discord.Embed.from_dict(json.loads(data['embed']))
    if data['madeby'] is not None:
        user = await ctx.bot.fetch_user(data['madeby'])
        embed.set_author(
            name=_("fun.gallery.send-meme.made_by", ctx, user=user),
            icon_url=user.avatar_url
        )
    embed.set_footer(
        text=_("fun.gallery.send_meme.sent", ctx, user=ctx.author),
        icon_url=ctx.author.avatar_url
    )
    if hidden:
        if ctx.channel is None:
            await ctx.author.send(embed=embed)
        else:
            await ctx.channel.send(embed=embed)

    else:
        await ctx.send(embed=embed)


class Gallery(commands.Cog):
    def __init__(self, gigachad) -> None:
        self.gigachad = gigachad

    @cog_ext.cog_subcommand(
        base="gallery",
        name="set-title",
        description="Change or set the title of a meme in your gallery!",
        options=[
            create_option(
                name="title",
                description="The new title that for the meme",
                required=True,
                option_type=3
            ),
            create_option(
                name="meme_id",
                description="The id of the meme, if not specified the latest meme title will be changed!",
                required=False,
                option_type=3
            )
        ]
    )
    async def gallery_set_title(self, ctx: SlashContext, title: str, meme_id: str = None) -> None:
        if meme_id is None:
            try:
                async with self.gigachad.db.acquire() as conn:
                    data = await conn.fetchrow("SELECT * FROM gallery WHERE usr = $1 ORDER BY time DESC", ctx.author.id)
                meme = dict(data)

            except TypeError:
                embed = create_embed(
                    author_text=_("fun.gallery.set_title.no_memes", ctx),
                    author_image=get_emote('no', type='image')
                )
                await ctx.send(embed=embed, hidden=True)
                return

        else:
            try:
                async with self.gigachad.db.acquire() as conn:
                    meme = dict(await conn.fetchrow("SELECT * FROM gallery WHERE id = $1", meme_id))

                if meme['usr'] != ctx.author.id:
                    embed = create_embed(
                        author_text=_("fun.gallery.set_title.others_meme.title", ctx),
                        author_image=get_emote('no', type='image'),
                        desc=_("fun.gallery.set_title.others_meme.desc", ctx, get_emote("dot"))
                    )
                    await ctx.send(embed=embed, hidden=True)
                    return

            except TypeError:
                embed = create_embed(
                    author_text=_("fun.gallery.set_title.unknown_meme", ctx),
                    author_image=get_emote('no', type='image')
                )
                await ctx.send(embed=embed, hidden=True)
                return

        embed = discord.Embed.from_dict(json.loads(meme['embed']))
        embed.title = (title[:97] + "...") if len(title) > 100 else title
        dict_embed = embed.to_dict()
        async with self.gigachad.db.acquire() as conn:
            await conn.execute(
                "UPDATE gallery SET embed = $1, title = $2 WHERE usr = $3 AND id = $4",
                json.dumps(dict_embed), embed.title, ctx.author.id, meme['id']
            )

        embed_to_send = create_embed(
            author_text=_("fun.gallery.set_title.success.title", ctx),
            author_image=get_emote('yes', type='image'),
            desc=_("fun.gallery.set_title.success.desc", ctx, dot=get_emote("dot"), id=str(meme['id']))
        )
        await ctx.send(embeds=[embed_to_send, embed])

    @cog_ext.cog_subcommand(
        base="gallery",
        name="send-meme",
        description="Send a meme from your gallery in the chat!",
        options=[create_option(
            name="meme_id",
            description="The id of the meme, if you don't know it don't specify it",
            required=False,
            option_type=3
        )]
    )
    async def gallery_send_meme(self, ctx: SlashContext, meme_id: str = None) -> None:
        if meme_id is None:
            async with self.gigachad.db.acquire() as conn:
                data = await conn.fetch("SELECT * FROM gallery WHERE usr = $1 ORDER BY time DESC", ctx.author.id)

            if not data:
                embed = create_embed(
                    author_text=_("fun.gallery.send_meme.no_memes", ctx),
                    author_image=get_emote('no', type='image')
                )
                await ctx.send(embed=embed, hidden=True)

            else:
                options = []
                dot = self.gigachad.get_emoji(get_emote("dot", type="id"))
                for r in data:
                    dict_r = dict(r)
                    options.append(
                        create_select_option(
                            label=dict_r['title'],
                            value=str(dict_r['id']),
                            description=f"ID: {str(dict_r['id'])} | Created: {datetime.fromtimestamp(dict_r['time'])}",
                            emoji=dot
                        )
                    )

                embed = create_embed(
                    author_text=_("fun.gallery.send_meme.meme_selection.title", ctx),
                    author_image=get_emote('gallery', type='image'),
                    desc=_("fun.gallery.send_meme.meme_selection.desc", ctx, dot=get_emote("dot"))
                )

                select = create_select(
                    options=options,
                    placeholder=_("fun.gallery.send_meme.meme_selection.select", ctx),
                    min_values=1,
                    max_values=1
                )
                await ctx.send(embed=embed, components=[create_actionrow(select)], hidden=True)

                selected_meme = await wait_for_component(self.gigachad, components=create_actionrow(select))

                async with self.gigachad.db.acquire() as conn:
                    data = dict(
                        await conn.fetchrow("SELECT * FROM gallery WHERE id = $1", selected_meme.selected_options[0])
                    )

                await send_meme(ctx, data, True)

                embed = create_embed(
                    author_text=_("fun.gallery.send_meme.meme_selection.success", ctx),
                    author_image=get_emote('yes', type='image')
                )
                await selected_meme.edit_origin(embed=embed, components=[])

        else:
            try:
                async with self.gigachad.db.acquire() as conn:
                    data = dict(await conn.fetchrow("SELECT * FROM gallery WHERE id = $1", meme_id))

                if data['usr'] != ctx.author.id:
                    return

                await send_meme(ctx, data)

            except TypeError:
                embed = create_embed(
                    author_text=_("fun.gallery.send_meme.unknow_meme.title", ctx),
                    author_image=get_emote('no', type='image'),
                    desc=_("fun.gallery.send_meme.unknow_meme.desc", ctx, get_emote("dot"))
                )
                await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base="gallery",
        name="open",
        description="Open your gallery"
    )
    async def gallery_open(self, ctx):
        paginator = GalleryPaginator(ctx=ctx, user=ctx.author)
        await paginator.run()

    @commands.Cog.listener()
    async def on_component(self, ctx: ComponentContext) -> None:
        if ctx.custom_id.startswith("save"):
            async with self.gigachad.db.acquire() as conn:
                count = dict(
                    await conn.fetchrow("SELECT COUNT(*) FROM gallery WHERE message = $1 AND usr = $2",
                                        ctx.origin_message_id, ctx.author.id)
                )
                total_count = dict(
                    await conn.fetchrow("SELECT COUNT(*) FROM gallery WHERE usr = $2",
                                        ctx.author.id)

                )
            if count['count'] != 0:
                embed = create_embed(
                    author_text=_("fun.gallery.save_meme.already_saved", ctx),
                    author_image=get_emote('no', type='image')
                )
                await ctx.send(embed=embed, hidden=True)

            elif total_count['count'] == 25:
                embed = create_embed(
                    author_text=_("fun.gallery.save_meme.too_much_memes.title", ctx),
                    author_image=get_emote('no', type='image'),
                    desc=_("fun.gallery.save_meme.too_much_memes.desc", ctx, dot=get_emote("dot"))
                )
                await ctx.send(embed=embed, hidden=True)

            else:
                component = create_actionrow(
                    create_button(
                        style=ButtonStyle.green,
                        label=_("fun.gallery.save_meme.confirm.buttons.confirm", ctx),
                        custom_id=f"confirm_{ctx.origin_message_id}_{ctx.custom_id.split('_')[1]}",
                        emoji=self.gigachad.get_emoji(get_emote("yes", type="id"))
                    ),
                    create_button(
                        style=ButtonStyle.red,
                        label=_("fun.gallery.save_meme.confirm.buttons.cancel", ctx),
                        custom_id="cancel",
                        emoji=self.gigachad.get_emoji(get_emote("no", type="id"))
                    )
                )
                embed = create_embed(
                    author_text=_("fun.gallery.save_meme.confirm.title", ctx),
                    author_image=get_emote('gallery', type='image'),
                    desc=_("fun.gallery.save_meme.confirm.desc", ctx, dot=get_emote("dot"), emote=get_emote("slash"))
                )
                await ctx.send(embed=embed, hidden=True, components=[component])

                button_ctx: ComponentContext = await wait_for_component(self.gigachad, components=component)

                if button_ctx.custom_id.startswith("confirm"):
                    key = await generate_key(self.gigachad)
                    msg = await ctx.channel.fetch_message(button_ctx.custom_id.split("_")[1])
                    embed = msg.embeds[0]
                    embed.timestamp = datetime.fromtimestamp(round(time.time()))

                    if embed.to_dict()['author']['name'] == "Click to access the post":
                        embed.remove_author()

                        url = "https://api.imgur.com/3/image"
                        payload = {'image': embed.image.url}
                        headers = {'Authorization': f'Client-ID {imgur_id}'}
                        async with aiohttp.ClientSession() as session:
                            async with session.post(url, data=payload, headers=headers) as r:
                                data = await r.read()
                        embed.set_image(url=json.loads(data)['data']['link'])

                        made_by = int(button_ctx.custom_id.split("_")[2])
                    else:
                        made_by = None

                    dict_embed = embed.to_dict()

                    if 'title' in dict_embed:
                        title = (dict_embed['title'][:97] + "...") if len(dict_embed['title']) > 100 else dict_embed[
                            'title']
                    else:
                        title = key

                    embed_to_send = create_embed(
                        author_text=_("fun.gallery.save_meme.success.title", ctx),
                        author_image=get_emote('yes', type='image'),
                        desc=_("fun.gallery.save_meme.success.desc", ctx, dot=get_emote("dot"), id=key, title=title,
                               emote=get_emote("slash"))
                    )
                    await button_ctx.edit_origin(embed=embed_to_send, components=[])

                    embed_to_reply = create_embed(
                        author_text=_("fun.gallery.save_meme.success.to_others", ctx, user=ctx.author),
                        author_image=get_emote('gallery', type='image')
                    )
                    await msg.reply(embed=embed_to_reply)

                    async with self.gigachad.db.acquire() as conn:
                        await conn.execute("INSERT INTO gallery (time, embed, title, usr, id, message, madeby) "
                                           "VALUES ($1, $2, $3, $4, $5, $6, $7)", round(time.time()),
                                           json.dumps(dict_embed), title, ctx.author_id, key, msg.id, made_by)

                else:
                    embed = create_embed(
                        author_text=_("fun.gallery.save_meme.canceled", ctx),
                        author_image=get_emote('yes', type='image')
                    )
                    await button_ctx.edit_origin(embed=embed, components=[])


class GalleryPaginator:
    def __init__(self, ctx, user):
        self.gigachad = ctx.bot
        self.user: discord.User = user
        self.ctx: discord_slash.context = ctx
        self.memes_pages: list = []
        self.top: int = 0
        self.index: int = 1
        self.msg: discord.Message = None
        self.delete_components = None
        self.delete = False
        self.memes_to_delete = None
        self.gallery_embed = create_embed(
            author_image=get_emote("gallery", type="image"),
            author_text="Your gallery",
            fields=[[_("fun.gallery.paginator.presentation.what_is_it.title", self.ctx),
                     _("fun.gallery.paginator.presentation.what_is_it.desc", self.ctx, dot=get_emote("dot"))],
                    [_("fun.gallery.paginator.presentation.what_is_it.how.title", self.ctx),
                     _("fun.gallery.paginator.presentation.what_is_it.how.desc", self.ctx, dot=get_emote("dot"),
                       button=get_emote("add"), slash=get_emote("slash"))]
                    ]
        )

    async def run(self) -> None:
        """" Runs the gallery paginator """
        async with self.gigachad.db.acquire() as conn:
            memes = await conn.fetch("SELECT * FROM gallery WHERE usr = $1 ORDER BY time DESC", self.user.id)

        if not memes:
            embed = create_embed(
                author_text="Ya got no memes in your gallery :/",
                author_image=get_emote("no", type="image")
            )
            await self.ctx.send(embeds=[self.gallery_embed, embed], hidden=True)
            return

        for meme in memes:
            embed = discord.Embed.from_dict(json.loads(meme['embed']))
            embed.set_footer(text=f"ID: {meme['id']} | Created at:")
            embed.timestamp = datetime.fromtimestamp(meme['time'])
            if meme['madeby'] is not None:
                user = await self.gigachad.fetch_user(meme['madeby'])
                embed.set_author(
                    name=f"Meme made by {user}",
                    icon_url=user.avatar_url
                )
            self.memes_pages.append(
                {'embed': embed,
                 'id': meme['id'],
                 'title': meme['title'],
                 'time': embed.timestamp}
            )

        self.top = len(self.memes_pages)
        self.msg = await self.ctx.send(
            embeds=[self.gallery_embed, self.memes_pages[0]['embed']],
            components=self.components()
        )

        while True:
            try:
                gallery_edit = False

                if self.delete:
                    button_ctx = await wait_for_component(
                        client=self.gigachad,
                        components=self.delete_components + self.components(),
                        timeout=10,
                        check=self.check
                    )
                else:
                    button_ctx = await wait_for_component(
                        client=self.gigachad,
                        messages=self.msg,
                        components=self.components(),
                        timeout=10,
                        check=self.check
                    )

                if button_ctx.custom_id == "first":
                    gallery_edit = True
                    self.index = 1
                elif button_ctx.custom_id == "prev":
                    self.index = self.index - 1 or 1
                    gallery_edit = True
                elif button_ctx.custom_id == "next":
                    gallery_edit = True
                    self.index = self.index + 1 or self.top
                elif button_ctx.custom_id == "last":
                    gallery_edit = True
                    self.index = self.top
                elif button_ctx.custom_id == "nav":
                    gallery_edit = True
                    self.index = int(button_ctx.selected_options[0])
                elif button_ctx.custom_id == "close":
                    embed = create_embed(
                        author_text=_("fun.gallery.paginator.closed", self.ctx),
                        author_image=get_emote('no', type='image')
                    )
                    await self.msg.edit(embed=embed, components=[])
                    return
                elif button_ctx.custom_id == "delete":
                    self.delete_components = await self.delete_memes(button_ctx)
                    await self.msg.edit(
                        embeds=[self.gallery_embed, self.memes_pages[self.index - 1]['embed']],
                        components=self.components()
                    )
                elif button_ctx.custom_id == "nav_delete":
                    self.memes_to_delete = button_ctx.selected_options
                    self.delete_components = await self.delete_memes_confirm(button_ctx)
                elif button_ctx.custom_id == "cancel":
                    embed = create_embed(
                        author_image=get_emote('yes', type="image"),
                        author_text=_("fun.gallery.paginator.deletion.cancel", self.ctx)
                    )
                    self.delete = False
                    await button_ctx.edit_origin(embed=embed, components=[])
                    await self.msg.edit(
                        embed=[self.gallery_embed, self.memes_pages[self.index - 1]['embed']],
                        components=self.components()
                    )
                elif button_ctx.custom_id == "confirm_delete":
                    async with self.gigachad.db.acquire() as conn:
                        for meme in self.memes_to_delete:
                            await conn.execute("DELETE FROM gallery WHERE ID = $1", meme)
                    embed = create_embed(
                        author_image=get_emote("yes", type="image"),
                        author_text=_("fun.gallery.paginator.deletion.success.title", self.ctx),
                        desc=_("fun.gallery.paginator.deletion.success.desc", self.ctx)
                    )
                    self.delete = False
                    await button_ctx.edit_origin(embed=embed, components=[])
                if gallery_edit:
                    await button_ctx.edit_origin(
                        embeds=[self.gallery_embed, self.memes_pages[self.index - 1]['embed']],
                        components=self.components()
                    )

            except asyncio.TimeoutError:
                components = self.components()
                for row in components:
                    for component in row["components"]:
                        component["disabled"] = True
                await self.msg.edit(components=components)
                return

    async def delete_memes(self, ctx: ComponentContext) -> list:
        embed = create_embed(
            author_text=_("fun.gallery.paginator.deletion.selection.title", self.ctx),
            author_image=get_emote("delete", type="image"),
            desc=_("fun.gallery.paginator.deletion.selection.desc", self.ctx)
        )
        button = [
            create_button(
                style=ButtonStyle.red,
                emoji=self.gigachad.get_emoji(get_emote("no", type='id')),
                label=_("fun.gallery.paginator.deletion.selection.buttons.cancel", self.ctx),
                custom_id="cancel"
            )
        ]
        select_options = []
        dot = self.gigachad.get_emoji(get_emote("dot", type="id"))
        for page in self.memes_pages:
            select_options.append(
                create_select_option(
                    label=page['title'],
                    description=_("fun.gallery.paginator.deletion.selection.buttons.navigator.select", self.ctx,
                                  id=page['id'], time=page['time']),
                    value=page['id'],
                    emoji=dot,
                )
            )
        select = create_select(
            options=select_options,
            placeholder=_("fun.gallery.paginator.deletion.selection.buttons.navigator.title", self.ctx),
            min_values=0,
            max_values=self.top,
            custom_id="nav_delete"
        )
        components = [create_actionrow(select), create_actionrow(*button)]
        await ctx.send(embed=embed, components=components, hidden=True)
        self.delete = True
        return components

    async def delete_memes_confirm(self, ctx: ComponentContext) -> list:
        embed = create_embed(
            author_image=get_emote("delete", type="image"),
            author_text=_("fun.gallery.paginator.deletion.confirmation.title", self.ctx),
            desc=_("fun.gallery.paginator.deletion.confirmation.desc", self.ctx)
        )
        buttons = [
            create_button(
                style=ButtonStyle.green,
                label=_("fun.gallery.paginator.deletion.confirmation.buttons.delete", self.ctx),
                custom_id="confirm_delete",
                emoji=self.gigachad.get_emoji(get_emote("delete", type='id'))
            ),
            create_button(
                style=ButtonStyle.red,
                label=_("fun.gallery.paginator.deletion.confirmation.buttons.cancel", self.ctx),
                custom_id="cancel",
                emoji=self.gigachad.get_emoji(get_emote("no", type='id'))
            )
        ]
        components = [create_actionrow(*buttons)]
        await ctx.edit_origin(embed=embed, components=components)
        return components

    def components(self) -> list:
        """ Returns the components to use within the gallery """
        disableLeft = self.index == 1
        disableRight = self.index == self.top
        nav_buttons = [
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("double_left", type='id')),
                disabled=disableLeft,
                custom_id="first"
            ),
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("left", type="id")),
                disabled=disableLeft,
                custom_id="prev"
            ),
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("right", type="id")),
                disabled=disableRight,
                custom_id="next"
            ),
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("double_right", type='id')),
                disabled=disableRight,
                custom_id="last"
            )
        ]
        disabled = True if self.delete is True else False
        action_buttons = [
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("no", type='id')),
                label=_("fun.gallery.paginator.buttons.close", self.ctx),
                custom_id="close"
            ),
            create_button(
                style=ButtonStyle.grey,
                emoji=self.gigachad.get_emoji(get_emote("delete", type='id')),
                label=_("fun.gallery.paginator.buttons.deletion", self.ctx),
                disabled=disabled,
                custom_id="delete"
            )
        ]
        dot = self.gigachad.get_emoji(get_emote("dot", type="id"))
        select_options = []
        for page in self.memes_pages:
            page_num = self.memes_pages.index(page) + 1
            select_options.append(
                create_select_option(
                    label=page['title'],
                    description=_("fun.gallery.paginator.buttons.navigator.select", self.ctx, page=page_num,
                                  total=self.top, id=page['id'], time=page['time']),
                    value=str(page_num),
                    emoji=dot
                )
            )

        select = create_select(
            options=select_options,
            placeholder=_("fun.gallery.paginator.buttons.navigator.title", self.ctx, page=self.index, total=self.top),
            min_values=1,
            max_values=1,
            custom_id="nav"
        )

        components = [create_actionrow(select), create_actionrow(*nav_buttons), create_actionrow(*action_buttons)]
        return components

    def check(self, button_ctx: ComponentContext) -> bool:
        return button_ctx.author == self.ctx.author


def setup(gigachad):
    gigachad.add_cog(Gallery(gigachad))
