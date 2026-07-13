from pyrogram.types import Message
from pyrogram import Client, filters, StopPropagation
from config import OWNER_ID, BOT_STATS_TEXT, USER_REPLY_TEXT, USER_ROAST, ADMINS
from datetime import datetime
from helper_func import get_readable_time
from database.database import full_userbase, count_users, is_admin

ADMIN_COMMANDS = [
    "addadmin", "deladmin", "admins",
    "reqtime", "reqmode", "approveoff", "approveon",
    "addchat", "addch", "delchat", "delch", "ch_links", "reqlink", "links", "bulklink", "genlink", "channels",
    "status", "cancel", "broadcast",
    "add_fsub", "del_fsub", "fsub",
    "stats", "ban"
]

@Client.on_message(filters.command(ADMIN_COMMANDS), group=-2)
async def admin_command_interceptor(bot: Client, message: Message):
    if not message.from_user:
        return
    
    user_id = message.from_user.id
    
    # Check if user is owner or admin
    is_authorized = (user_id == OWNER_ID) or (user_id in ADMINS) or (await is_admin(user_id))
    
    if not is_authorized:
        command = message.command[0].lower() if message.command else ""
        if command in ["ban", "broadcast"]:
            if USER_ROAST:
                await message.reply_text(USER_ROAST)
        else:
            if USER_REPLY_TEXT:
                await message.reply_text(USER_REPLY_TEXT)
        
        # Stop further handling of this message
        raise StopPropagation

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
