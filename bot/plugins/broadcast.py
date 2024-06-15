import asyncio
import time
import datetime
from pyrogram.types import Message
from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.enums import ChatAction
from bot import SUDO_USERS
from bot import LOGGER
from bot.db.broadcast_sql import query_msg, del_user


@Client.on_message(
    filters.private & filters.command("stats") & filters.user(SUDO_USERS)
)
async def get_subscribers_count(bot: Client, message: Message):
    wait_msg = "__Calculating, please wait...__"
    msg = await message.reply_text(wait_msg, quote=True)
    active, blocked = await users_info(bot)
    stats_msg = f"**Stats**\nSubscribers: `{active}`\nBlocked / Deleted: `{blocked}`"
    await msg.edit(stats_msg)


@Client.on_message(
    filters.private & filters.command("broadcast") & filters.user(SUDO_USERS)
)
async def send_text(bot, message: Message):
    user_id = message.from_user.id
    if "broadcast" in message.text and message.reply_to_message is not None:
        start_time = time.time()
        await message.reply_text("Starting broadcast, content below...", quote=True)
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.reply_to_message_id,
            reply_markup=message.reply_to_message.reply_markup,
        )
        query = await query_msg()
        success = 0
        failed = 0
        for row in query:
            chat_id = int(row[0])
            br_msg = bool()
            try:
                br_msg = await bot.copy_message(
                    chat_id=chat_id,
                    from_chat_id=message.chat.id,
                    message_id=message.reply_to_message_id,
                    reply_markup=message.reply_to_message.reply_markup,
                )
                LOGGER.info("Broadcast sent to %s", chat_id)
            except FloodWait as e:
                LOGGER.warning("Floodwait while broadcasting, sleeping for %s", e.value)
                await asyncio.sleep(e.value)
            except Exception:
                pass

            if bool(br_msg):
                success += 1
            else:
                failed += 1
        time_taken = datetime.timedelta(seconds=int(time.time() - start_time))
        await message.reply_text(
            f"**Broadcast Completed**\nSent to: `{success}`\nBlocked / Deleted: `{failed}`\nCompleted in `{time_taken}` hh:mm:ss",
            quote=True,
        )

    else:
        reply_error = (
            "`Use this command as a reply to any telegram message without any spaces.`"
        )
        msg = await message.reply_text(reply_error, message.id, quote=True)
        await asyncio.sleep(8)
        await msg.delete()


async def users_info(bot):
    users = 0
    blocked = 0
    identity = await query_msg()
    for user in identity:
        user_id = int(user[0])
        name = bool()
        try:
            name = await bot.send_chat_action(user_id, ChatAction.TYPING)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except Exception:
            pass
        if bool(name):
            users += 1
        else:
            await del_user(user_id)
            LOGGER.info("Deleted user id %s from broadcast list", user_id)
            blocked += 1
    return users, blocked
