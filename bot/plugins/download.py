import os
from time import sleep
from pyrogram import Client, filters
from bot.helpers.sql_helper import gDriveDB, idsDB
from bot.helpers.utils import CustomFilters, humanbytes
from bot.helpers.downloader import download_file, utube_dl
from bot.helpers.gdrive_utils import GoogleDrive
from bot import DOWNLOAD_DIRECTORY, LOGGER
from bot.config import Messages, BotCommands
from pyrogram.errors import FloodWait, RPCError
from bot.plugins.forcesub import check_forcesub
from bot.db.ban_sql import is_banned


@Client.on_message(
    filters.private
    & filters.incoming
    & filters.text
    & (filters.command(BotCommands.Download) | filters.regex("^(ht|f)tp*"))
    & CustomFilters.auth_users
)
async def _download(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return

    if not message.media:
        sent_message = await message.reply_text("🕵️**Checking link...**", quote=True)
        if message.command:
            link = message.command[1]
        else:
            link = message.text
        if "drive.google.com" in link:
            await sent_message.edit(Messages.CLONING.format(link))
            LOGGER.info(f"Copy:{user_id}: {link}")
            msg = GoogleDrive(user_id).clone(link)
            await sent_message.edit(msg)
        else:
            if "|" in link:
                link, filename = link.split("|")
                link = link.strip()
                filename.strip()
                dl_path = os.path.join(f"{DOWNLOAD_DIRECTORY}/{filename}")
            else:
                link = link.strip()
                filename = os.path.basename(link)
                dl_path = DOWNLOAD_DIRECTORY
            LOGGER.info(f"Download:{user_id}: {link}")
            await sent_message.edit(Messages.DOWNLOADING.format(link))
            result, file_path = download_file(link, dl_path)
            if result == True:
                await sent_message.edit(
                    Messages.DOWNLOADED_SUCCESSFULLY.format(
                        os.path.basename(file_path),
                        humanbytes(os.path.getsize(file_path)),
                    )
                )
                msg = GoogleDrive(user_id).upload_file(file_path)
                await sent_message.edit(msg)
                LOGGER.info(f"Deleteing: {file_path}")
                os.remove(file_path)
            else:
                await sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))


@Client.on_message(
    filters.private
    & filters.incoming
    & (filters.document | filters.audio | filters.video | filters.photo)
    & CustomFilters.auth_users
)
async def _telegram_file(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return

    sent_message = await message.reply_text("🕵️**Checking File...**", quote=True)
    if message.document:
        file = message.document
    elif message.video:
        file = message.video
    elif message.audio:
        file = message.audio
    elif message.photo:
        file = message.photo
        file.mime_type = "images/png"
        file.file_name = f"IMG-{user_id}-{message.id}.png"
    await sent_message.edit(
        Messages.DOWNLOAD_TG_FILE.format(
            file.file_name, humanbytes(file.file_size), file.mime_type
        )
    )
    LOGGER.info(f"Download:{user_id}: {file.file_name}")
    try:
        file_path = await message.download(file_name=DOWNLOAD_DIRECTORY)
        await sent_message.edit(
            Messages.DOWNLOADED_SUCCESSFULLY.format(
                os.path.basename(file_path), humanbytes(os.path.getsize(file_path))
            )
        )
        msg = GoogleDrive(user_id).upload_file(file_path, file.mime_type)
        await sent_message.edit(msg)
    except RPCError:
        await sent_message.edit(Messages.WENT_WRONG)
    LOGGER.info(f"Deleteing: {file_path}")
    os.remove(file_path)


@Client.on_message(
    filters.incoming
    & filters.private
    & filters.command(BotCommands.YtDl)
    & CustomFilters.auth_users
)
async def _ytdl(client, message):
    user_id = message.from_user.id

    if await is_banned(user_id):
        await message.reply_text("You are banned from using this bot.", quote=True)
        return

    if not await check_forcesub(client, message, user_id):
        return
    if len(message.command) > 1:
        sent_message = await message.reply_text("🕵️**Checking Link...**", quote=True)
        link = message.command[1]
        LOGGER.info(f"YTDL:{user_id}: {link}")
        await sent_message.edit(Messages.DOWNLOADING.format(link))
        result, file_path = utube_dl(link)
        if result:
            await sent_message.edit(
                Messages.DOWNLOADED_SUCCESSFULLY.format(
                    os.path.basename(file_path), humanbytes(os.path.getsize(file_path))
                )
            )
            msg = GoogleDrive(user_id).upload_file(file_path)
            await sent_message.edit(msg)
            LOGGER.info(f"Deleteing: {file_path}")
            os.remove(file_path)
        else:
            await sent_message.edit(Messages.DOWNLOAD_ERROR.format(file_path, link))
    else:
        await message.reply_text(Messages.PROVIDE_YTDL_LINK, quote=True)
