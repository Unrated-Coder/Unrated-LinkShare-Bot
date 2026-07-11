# Upgraded by @Unrated_Coder from Telegram
from pyrogram import Client, filters
from pyrogram.types import Message
from config import OWNER_ID, ADMINS
from database.database import add_fsub_channel, remove_fsub_channel, get_fsub_channels
from helper_func import is_owner_or_admin

@Client.on_message(filters.command("add_fsub") & is_owner_or_admin)
async def add_fsub_cmd(client: Client, message: Message):
    if len(message.command) < 2:
        return await message.reply_text("<b>Usage:</b> <code>/add_fsub {channel_id} {mode}</code>\n\n<b>Modes:</b> <code>normal</code> (default), <code>request</code>")

    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("<b>Invalid Channel ID.</b>")

    mode = "normal"
    if len(message.command) >= 3:
        mode = message.command[2].lower()
        if mode not in ["normal", "request"]:
            return await message.reply_text("<b>Invalid Mode. Use <code>normal</code> or <code>request</code>.</b>")

    try:
        chat = await client.get_chat(channel_id)
    except Exception as e:
        return await message.reply_text(f"<b>Error:</b> <code>{e}</code>\nMake sure I am admin in that channel.")

    success = await add_fsub_channel(channel_id, mode)
    if success:
        await message.reply_text(f"✅ <b>Successfully added to FSub:</b>\n\n<b>Title:</b> {chat.title}\n<b>ID:</b> <code>{channel_id}</code>\n<b>Mode:</b> <code>{mode}</code>")
    else:
        await message.reply_text("❌ <b>Failed to add channel to FSub.</b>")

@Client.on_message(filters.command("del_fsub") & is_owner_or_admin)
async def del_fsub_cmd(client: Client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text("<b>Usage:</b> <code>/del_fsub {channel_id}</code>")

    try:
        channel_id = int(message.command[1])
    except ValueError:
        return await message.reply_text("<b>Invalid Channel ID.</b>")

    success = await remove_fsub_channel(channel_id)
    if success:
        await message.reply_text(f"✅ <b>Removed <code>{channel_id}</code> from FSub list.</b>")
    else:
        await message.reply_text("❌ <b>Channel not found in FSub list.</b>")

@Client.on_message(filters.command("fsub") & is_owner_or_admin)
async def list_fsub_cmd(client: Client, message: Message):
    channels = await get_fsub_channels()
    if not channels:
        return await message.reply_text("<b>No channels in FSub list.</b>")

    text = "<b>📢 Force Subscription Channels:</b>\n\n"
    for i, ch in enumerate(channels, 1):
        try:
            chat = await client.get_chat(ch['channel_id'])
            title = chat.title
        except:
            title = "Unknown"
        text += f"{i}. <b>{title}</b>\n   ID: <code>{ch['channel_id']}</code>\n   Mode: <code>{ch.get('mode', 'normal')}</code>\n\n"

    await message.reply_text(text)
