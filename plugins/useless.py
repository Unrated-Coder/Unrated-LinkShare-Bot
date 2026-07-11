from pyrogram.types import Message
from pyrogram import Client, filters
from config import OWNER_ID, BOT_STATS_TEXT, USER_REPLY_TEXT
from datetime import datetime
from helper_func import get_readable_time
from database.database import full_userbase, count_users

# --- 1. NORMAL USER KE LIYE AUTO-REPLY ---
# Isme humne commands ko exclude kar diya hai (~filters.command)
@Client.on_message(filters.private & filters.incoming & filters.text & ~filters.regex(r"^/"))
async def useless_reply(bot: Client, message: Message):
    user_id = message.from_user.id
    if user_id != OWNER_ID: # Sirf unko reply jaye jo owner nahi hain
        if USER_REPLY_TEXT:
            await message.reply_text(USER_REPLY_TEXT)

# --- 2. STATS COMMAND (WITH SECURITY) ---
@Client.on_message(filters.command('stats') & filters.private)
async def stats(bot: Client, message: Message):
    user_id = message.from_user.id
    
    # AGAR NORMAL USER HAI
    if user_id != OWNER_ID:
        if USER_REPLY_TEXT:
            await message.reply_text(USER_REPLY_TEXT)
        return

    # AGAR OWNER HAI
    now = datetime.now()
    delta = now - bot.uptime
    uptime_time = get_readable_time(delta.seconds)
    
    wait_msg = await message.reply_text("<code>📊 Processing Stats...</code>")
    
    try:
        total_users = await count_users()
    except:
        total_users = "Error"

    final_text = (
        "<b>📊 ʟɪɴᴋ sʜᴀʀᴇ ʙᴏᴛ sᴛᴀᴛs</b>\n\n"
        f"<b>🚀 ᴜᴘᴛɪᴍᴇ:</b> <code>{uptime_time}</code>\n"
        f"<b>👤 ᴛᴏᴛᴀʟ ᴜsᴇʀs:</b> <code>{total_users}</code>\n"
        f"<b>🔐 ᴀᴄᴄᴇss:</b> ꜰᴜʟʟ ᴄᴏɴᴛʀᴏʟ"
    )
    await wait_msg.edit_text(final_text)
