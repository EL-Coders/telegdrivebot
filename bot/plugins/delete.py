from pyrogram import Client, filters
from bot.config import BotCommands, Messages
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.utils import CustomFilters
from bot import LOGGER
from bot.plugins.forcesub import check_forcesub
from bot.db.ban_sql import is_banned


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(BotCommands.Delete)
    & CustomFilters.auth_users
)
async def _delete(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return

    if len(message.command) > 1 or message.reply_to_message:
        sent_message = await message.reply_text("🕵️**Checking Link...**", quote=True)
        if len(message.command) > 1:
            link = message.command[1]
        elif message.reply_to_message.entities[1].url:
            link = message.reply_to_message.entities[1].url
        else:
            await message.reply_text(
                Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Delete[0]), quote=True
            )
            return
        LOGGER.info(f"Delete:{user_id}: {link}")
        result = GoogleDrive(user_id).delete_file(link)
        await sent_message.edit(result)
    else:
        await message.reply_text(
            Messages.PROVIDE_GDRIVE_URL.format(BotCommands.Delete[0]), quote=True
        )


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(BotCommands.EmptyTrash)
    & CustomFilters.auth_users
)
async def _emptyTrash(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return

    LOGGER.info(f"EmptyTrash: {user_id}")
    msg = GoogleDrive(user_id).emptyTrash()
    await message.reply_text(msg, quote=True)
