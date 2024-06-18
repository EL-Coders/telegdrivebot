from pyrogram import Client, filters
from bot.config import BotCommands
from bot.helpers.gdrive_utils import GoogleDrive
from bot.helpers.utils import CustomFilters
from bot import LOGGER
from bot.plugins.forcesub import check_forcesub
from bot.db.ban_sql import is_banned
from bot.helpers.sql_helper import idsDB


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.command(BotCommands.ListFiles)
    & CustomFilters.auth_users
)
async def _listFiles(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return

    parent = idsDB.search_parent(user_id)
    if parent is None:
        await message.reply_text("Parent not found", quote=True)
        return

    files = GoogleDrive(user_id).getFilesByFolderId(parent)
    if len(files) == 0:
        await message.reply_text("No files found", quote=True)
        return

    files_msg = ">Name - ID\n"
    for file in files:
        files_msg += f"`{file.get('name')}` - `{file.get('id')}`\n"
    await message.reply_text(files_msg, quote=True)
