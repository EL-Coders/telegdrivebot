from pyrogram import Client, filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from pyrogram.enums import ParseMode, ChatMemberStatus
from pyrogram.errors import UserNotParticipant
from bot import LOGGER, SUDO_USERS
from bot.db.forcesub_sql import set_channel, get_link, get_channel, delete_channel


@Client.on_message(filters.command(["forcesub"]) & filters.user(SUDO_USERS))
async def force_sub(bot, update):
    data = update.text.split()
    if len(data) == 2:
        channel_id = data[-1]
        if channel_id.lower() == "off":
            channel_id = 0

        if channel_id:
            try:
                link = await bot.create_chat_invite_link(channel_id)
                await set_channel(channel_id, link.invite_link)
                await update.reply_text(
                    f"Force Subscription channel set to `{channel_id} with invite link: {link.invite_link}`",
                    quote=True,
                )
            except Exception as e:
                await update.reply_text(
                    f" Error while creating channel invite link: {str(e)}", quote=True
                )
                return
        else:
            await delete_channel()
            await update.reply_text("Force Subscription disabled", quote=True)

    else:
        await update.reply_text(
            "Please send in proper format `/forcesub channel_id/off`", quote=True
        )


@Client.on_message(filters.command(["checklink"]) & filters.user(SUDO_USERS))
async def testlink(bot, update):
    link = await get_link()
    if link:
        await update.reply_text(
            f"Invite link for force subscription channel: {link}", quote=True
        )
    else:
        await update.reply_text(
            "Force Subscription is disabled, please enable it first", quote=True
        )


async def check_forcesub(bot, message, user_id):
    force_sub = await get_channel()
    if force_sub:
        try:
            user = await bot.get_chat_member(int(force_sub), user_id)
            if user.status == ChatMemberStatus.BANNED:
                await message.reply_text("Sorry, you are Banned to use me.", quote=True)
                return False
        except UserNotParticipant:
            link = await get_link()
            await message.reply_text(
                text=">Please join my Update Channel to use this Bot!",
                reply_markup=InlineKeyboardMarkup(
                    [[InlineKeyboardButton("🤖 Join Channel", url=link)]]
                ),
                parse_mode=ParseMode.MARKDOWN,
                quote=True,
            )
            return False
        except Exception as e:
            LOGGER.warning(e)
            await message.reply_text(
                text="Something went wrong, please contact my support group",
                quote=True,
            )
            return False
    return True
