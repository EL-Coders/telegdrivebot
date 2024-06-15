from bot import SUPPORT_CHAT_LINK
from pyrogram import Client, filters
from bot.config import Messages as tr
from bot.db.broadcast_sql import add_user
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


START_KB = InlineKeyboardMarkup(
    [
        [
            InlineKeyboardButton("🌿 Source Code", url="https://github.com/EL-Coders/telegdrivebot"),
            InlineKeyboardButton("👨‍💻 Maintainer", url="https://t.me/jithumon"),
        ],
        [InlineKeyboardButton("📢 Update Channel", url="https://t.me/ELUpdates")],
    ]
)


@Client.on_message(
    filters.private & filters.incoming & filters.command(["start"]), group=2
)
async def _start(client, message):
    user_id = message.from_user.id
    user_name = "@" + message.from_user.username if message.from_user.username else None
    await add_user(user_id, user_name)

    await client.send_message(
        chat_id=message.chat.id,
        text=tr.START_MSG.format(message.from_user.mention),
        reply_to_message_id=message.id,
        reply_markup=START_KB,
    )


@Client.on_message(
    filters.private & filters.incoming & filters.command(["help"]), group=2
)
async def _help(client, message):
    user_id = message.from_user.id
    user_name = "@" + message.from_user.username if message.from_user.username else None
    await add_user(user_id, user_name)

    await client.send_message(
        chat_id=message.chat.id,
        text=tr.HELP_MSG[1],
        reply_markup=InlineKeyboardMarkup(map(1)),
        reply_to_message_id=message.id,
    )


help_callback_filter = filters.create(
    lambda _, __, query: query.data.startswith("help+")
)


@Client.on_callback_query(help_callback_filter)
async def help_answer(c, callback_query):
    chat_id = callback_query.from_user.id
    message_id = callback_query.message.id
    msg = int(callback_query.data.split("+")[1])
    await c.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=tr.HELP_MSG[msg],
        reply_markup=InlineKeyboardMarkup(map(msg)),
    )


def map(pos):
    if pos == 1:
        button = [[InlineKeyboardButton(text="-->", callback_data="help+2")]]
    elif pos == len(tr.HELP_MSG) - 1:
        button = [
            [
                InlineKeyboardButton(text="Support Chat", url=SUPPORT_CHAT_LINK),
                InlineKeyboardButton(text="Feature Request", url="t.me/elsupport"),
            ],
            [InlineKeyboardButton(text="<--", callback_data=f"help+{pos-1}")],
        ]
    else:
        button = [
            [
                InlineKeyboardButton(text="<--", callback_data=f"help+{pos-1}"),
                InlineKeyboardButton(text="-->", callback_data=f"help+{pos+1}"),
            ],
        ]
    return button
