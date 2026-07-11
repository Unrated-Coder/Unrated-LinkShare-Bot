# Upgraded by @Unrated_Coder from Telegram
import asyncio
import base64
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.errors import UserNotParticipant, FloodWait, ChatAdminRequired, RPCError
from pyrogram.errors import InviteHashExpired, InviteRequestSent
from database.database import save_channel, delete_channel, get_channels
from config import *
from database.database import *
from helper_func import *
from datetime import datetime, timedelta

PAGE_SIZE = 6

# Cache for chat information to avoid repeated API calls
chat_info_cache = {}

# Revoke invite link after 5-10 minutes
async def revoke_invite_after_5_minutes(client: Client, channel_id: int, link: str, is_request: bool = False):
    await asyncio.sleep(300)  # 5 minutes
    try:
        await client.revoke_chat_invite_link(channel_id, link)
        print(f"{'Jᴏɪɴ ʀᴇǫᴜᴇsᴛ' if is_request else 'Iɴᴠɪᴛᴇ'} ʟɪɴᴋ ʀᴇᴠᴏᴋᴇᴅ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}")
    except (InviteHashExpired, RPCError) as e:
        print(f"Link already revoked or expired for {channel_id}: {e}")
    except Exception as e:
        print(f"Fᴀɪʟᴇᴅ ᴛᴏ ʀᴇᴠᴏᴋᴇ ɪɴᴠɪᴛᴇ ғᴏʀ ᴄʜᴀɴɴᴇʟ {channel_id}: {e}")

# Add chat command
@Client.on_message((filters.command('addchat') | filters.command('addch')) & is_owner_or_admin)
async def set_channel(client: Client, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply("<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ID. Exᴀᴍᴘʟᴇ: <code>/addchat &lt;chat_id&gt;</code></b>")

    try:
        chat = await client.get_chat(channel_id)

        # Check permissions based on chat type
        if chat.permissions:
            # For groups/channels, check appropriate permissions
            has_permission = False
            if hasattr(chat.permissions, 'can_post_messages') and chat.permissions.can_post_messages:
                has_permission = True
            elif hasattr(chat.permissions, 'can_edit_messages') and chat.permissions.can_edit_messages:
                has_permission = True
            elif chat.type.name in ['GROUP', 'SUPERGROUP']:
                # For groups, having the bot as admin is usually sufficient
                try:
                    bot_member = await client.get_chat_member(chat.id, (await client.get_me()).id)
                    if bot_member.status.name in ['ADMINISTRATOR', 'CREATOR']:
                        has_permission = True
                except:
                    pass

            if not has_permission:
                return await message.reply(f"<b><blockquote expandable>I ᴀᴍ ɪɴ {chat.title}, ʙᴜᴛ I ʟᴀᴄᴋ ᴘᴏsᴛɪɴɢ ᴏʀ ᴇᴅɪᴛɪɴɢ ᴘᴇʀᴍɪssɪᴏɴs.</b>")

        await save_channel(channel_id)
        base64_invite = await save_encoded_link(channel_id)
        normal_link = f"https://t.me/{client.username}?start={base64_invite}"
        base64_request = await encode(str(channel_id))
        await save_encoded_link2(channel_id, base64_request)
        request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
        reply_text = (
            f"<b><blockquote expandable>✅ Cʜᴀᴛ {chat.title} ({channel_id}) ʜᴀs ʙᴇᴇɴ ᴀᴅᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>\n\n"
            f"<b>🔗 Nᴏʀᴍᴀʟ Lɪɴᴋ:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Rᴇǫᴜᴇsᴛ Lɪɴᴋ:</b> <code>{request_link}</code>"
        )
        return await message.reply(reply_text)

    except UserNotParticipant:
        return await message.reply("<b><blockquote expandable>I ᴀᴍ ɴᴏᴛ ᴀ ᴍᴇᴍʙᴇʀ ᴏғ ᴛʜɪs ᴄʜᴀɴɴᴇʟ. Pʟᴇᴀsᴇ ᴀᴅᴅ ᴍᴇ ᴀɴᴅ ᴛʀʏ ᴀɢᴀɪɴ.</b>")
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await set_channel(client, message)
    except RPCError as e:
        return await message.reply(f"RPC Error: {str(e)}")
    except Exception as e:
        return await message.reply(f"Unexpected Error: {str(e)}")

# Delete chat command
@Client.on_message((filters.command('delchat') | filters.command('delch')) & is_owner_or_admin)
async def del_channel(client: Client, message: Message):
    try:
        channel_id = int(message.command[1])
    except (IndexError, ValueError):
        return await message.reply("<b><blockquote expandable>Iɴᴠᴀʟɪᴅ ᴄʜᴀᴛ ID. Exᴀᴍᴘʟᴇ: <code>/delch &lt;chat_id&gt;</code></b>")

    await delete_channel(channel_id)
    return await message.reply(f"<b><blockquote expandable>❌ Cʜᴀᴛ {channel_id} ʜᴀs ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.</b>")

# Channel post command
@Client.on_message(filters.command('ch_links') & is_owner_or_admin)
async def channel_post(client: Client, message: Message):
    try:
        channels = await get_channels()
        if not channels:
            return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")

        await send_channel_page(client, message, channels, page=0)
    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{str(e)}</code>")

async def send_channel_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []

    # Get all chat info concurrently
    chat_tasks = []
    for channel_id in channels[start_idx:end_idx]:
        chat_tasks.append(get_chat_info(client, channel_id))

    try:
        chat_infos = await asyncio.gather(*chat_tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error gathering chat info: {e}")
        chat_infos = [None] * len(channels[start_idx:end_idx])

    row = []
    for i, chat_info in enumerate(chat_infos):
        channel_id = channels[start_idx + i]
        if isinstance(chat_info, Exception) or chat_info is None:
            print(f"Error getting chat info for channel {channel_id}: {chat_info}")
            continue

        try:
            base64_invite = await save_encoded_link(channel_id)
            button_link = f"https://t.me/{client.username}?start={base64_invite}"

            row.append(InlineKeyboardButton(chat_info.title, url=button_link))

            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception as e:
            print(f"Error for channel {channel_id}: {e}")

    if row:
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelpage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴀᴄᴄᴇss:", reply_markup=reply_markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴄʜᴀɴɴᴇʟ:", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"channelpage_(\d+)"))
async def paginate_channels(client: Client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_channel_page(client, callback_query.message, channels, page, edit=True)

# Request post command
@Client.on_message(filters.command('reqlink') & is_owner_or_admin)
async def req_post(client: Client, message: Message):
    try:
        channels = await get_channels()
        if not channels:
            return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /setchannel ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ</b>")

        await send_request_page(client, message, channels, page=0)
    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{str(e)}</code>")

async def send_request_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE
    buttons = []

    # Get all chat info concurrently
    chat_tasks = []
    for channel_id in channels[start_idx:end_idx]:
        chat_tasks.append(get_chat_info(client, channel_id))

    try:
        chat_infos = await asyncio.gather(*chat_tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error gathering chat info: {e}")
        chat_infos = [None] * len(channels[start_idx:end_idx])

    row = []
    for i, chat_info in enumerate(chat_infos):
        channel_id = channels[start_idx + i]
        if isinstance(chat_info, Exception) or chat_info is None:
            print(f"Error getting chat info for channel {channel_id}: {chat_info}")
            continue

        try:
            base64_request = await encode(str(channel_id))
            await save_encoded_link2(channel_id, base64_request)
            button_link = f"https://t.me/{client.username}?start=req_{base64_request}"

            row.append(InlineKeyboardButton(chat_info.title, url=button_link))

            if len(row) == 2:
                buttons.append(row)
                row = []
        except Exception as e:
            print(f"Error generating request link for channel {channel_id}: {e}")

    if row:
        buttons.append(row)

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"reqpage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"reqpage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)
    reply_markup = InlineKeyboardMarkup(buttons)
    if edit:
        await message.edit_text("Sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ʀᴇǫᴜᴇsᴛ ᴀᴄᴄᴇss:", reply_markup=reply_markup)
    else:
        await message.reply("Sᴇʟᴇᴄᴛ ᴄʜᴀɴɴᴇʟ:", reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"reqpage_(\d+)"))
async def paginate_requests(client: Client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_request_page(client, callback_query.message, channels, page, edit=True)

# Links command - show all links as text
@Client.on_message(filters.command('links') & is_owner_or_admin)
async def show_links(client: Client, message: Message):
    try:
        channels = await get_channels()
        if not channels:
            return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")

        await send_links_page(client, message, channels, page=0)
    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{str(e)}</code>")

async def send_links_page(client, message, channels, page, edit=False):
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    links_text = "<b>➤ Aʟʟ Cʜᴀɴɴᴇʟ Lɪɴᴋs:</b>\n\n"

    # Get all chat info and links concurrently
    tasks = []
    for channel_id in channels[start_idx:end_idx]:
        tasks.append(asyncio.gather(
            get_chat_info(client, channel_id),
            save_encoded_link(channel_id),
            asyncio.create_task(encode(str(channel_id))),
            return_exceptions=True
        ))

    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error gathering link info: {e}")
        results = [None] * len(channels[start_idx:end_idx])

    for i, result in enumerate(results):
        idx = start_idx + i + 1
        channel_id = channels[start_idx + i]

        if isinstance(result, Exception) or result is None or any(isinstance(r, Exception) for r in result):
            print(f"Error getting info for channel {channel_id}: {result}")
            links_text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n\n"
            continue

        try:
            chat_info, base64_invite, base64_request = result
            if isinstance(chat_info, Exception):
                links_text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n\n"
                continue

            await save_encoded_link2(channel_id, base64_request)
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            request_link = f"https://t.me/{client.username}?start=req_{base64_request}"

            links_text += f"<b>{idx}. {chat_info.title}</b>\n"
            links_text += f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            links_text += f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"

        except Exception as e:
            print(f"Error for channel {channel_id}: {e}")
            links_text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n\n"

    # Add pagination info
    links_text += f"<b>📄 Pᴀɢᴇ {page + 1} ᴏғ {total_pages}</b>"

    # Create navigation buttons
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"linkspage_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"linkspage_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None

    if edit:
        await message.edit_text(links_text, reply_markup=reply_markup)
    else:
        await message.reply(links_text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"linkspage_(\d+)"))
async def paginate_links(client: Client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_links_page(client, callback_query.message, channels, page, edit=True)

# Bulk link generation command
@Client.on_message(filters.command('bulklink') & is_owner_or_admin)
async def bulk_link(client: Client, message: Message):
    user_id = message.from_user.id

    if len(message.command) < 2:
        return await message.reply("<b><blockquote expandable>ᴜsᴀɢᴇ: <code>/bulklink &lt;id1&gt; &lt;id2&gt; ...</code></b>")

    ids = message.command[1:]
    reply_text = "<b>➤ Bᴜʟᴋ Lɪɴᴋ Gᴇɴᴇʀᴀᴛɪᴏɴ:</b>\n\n"
    for idx, id_str in enumerate(ids, start=1):
        try:
            channel_id = int(id_str)
            chat = await client.get_chat(channel_id)
            base64_invite = await save_encoded_link(channel_id)
            normal_link = f"https://t.me/{client.username}?start={base64_invite}"
            base64_request = await encode(str(channel_id))
            await save_encoded_link2(channel_id, base64_request)
            request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
            reply_text += f"<b>{idx}. {chat.title} ({channel_id})</b>\n"
            reply_text += f"<b>➥ Nᴏʀᴍᴀʟ:</b> <code>{normal_link}</code>\n"
            reply_text += f"<b>➤ Rᴇǫᴜᴇsᴛ:</b> <code>{request_link}</code>\n\n"
        except Exception as e:
            reply_text += f"<b>{idx}. Channel {id_str}</b> (Error: {e})\n\n"
    await message.reply(reply_text)

@Client.on_message(filters.command('genlink') & filters.private & is_owner_or_admin)
async def generate_link_command(client: Client, message: Message):
    user_id = message.from_user.id
    if len(message.command) < 2:
        return await message.reply("<b>Usage:</b> <code>/genlink &lt;link&gt;</code>")

    link = message.command[1]
    # Store the link in the database channel
    try:
        sent_msg = await client.send_message(DATABASE_CHANNEL, f"#LINK\n{link}")
        channel_id = sent_msg.id  # Use id as unique id for this link
        # Save encoded links
        base64_invite = await save_encoded_link(channel_id)
        base64_request = await encode(str(channel_id))
        await save_encoded_link2(channel_id, base64_request)
        # Store the original link in the database
        from database.database import channels_collection
        await channels_collection.update_one(
            {"channel_id": channel_id},
            {"$set": {"original_link": link}},
            upsert=True
        )
        normal_link = f"https://t.me/{client.username}?start={base64_invite}"
        request_link = f"https://t.me/{client.username}?start=req_{base64_request}"
        reply_text = (
            f"<b>✅ Link stored and encoded successfully.</b>\n\n"
            f"<b>🔗 Normal Link:</b> <code>{normal_link}</code>\n"
            f"<b>🔗 Request Link:</b> <code>{request_link}</code>"
        )
        await message.reply(reply_text)
    except Exception as e:
        await message.reply(f"<b>Error storing link:</b> <code>{e}</code>")

@Client.on_message(filters.command('channels') & is_owner_or_admin)
async def show_channel_ids(client: Client, message: Message):
    try:
        channels = await get_channels()
        if not channels:
            return await message.reply("<b><blockquote expandable>Nᴏ ᴄʜᴀɴɴᴇʟs ᴀʀᴇ ᴀᴠᴀɪʟᴀʙʟᴇ. Pʟᴇᴀsᴇ ᴜsᴇ /addch ᴛᴏ ᴀᴅᴅ ᴀ ᴄʜᴀɴɴᴇʟ.</b>")

        await send_channel_ids_page(client, message, channels, page=0)
    except Exception as e:
        await message.reply(f"<b>Error:</b> <code>{str(e)}</code>")

async def send_channel_ids_page(client, message, channels, page, edit=False):
    PAGE_SIZE = 10
    total_pages = (len(channels) + PAGE_SIZE - 1) // PAGE_SIZE
    start_idx = page * PAGE_SIZE
    end_idx = start_idx + PAGE_SIZE

    # Get all chat info concurrently
    chat_tasks = []
    for channel_id in channels[start_idx:end_idx]:
        chat_tasks.append(get_chat_info(client, channel_id))

    try:
        chat_infos = await asyncio.gather(*chat_tasks, return_exceptions=True)
    except Exception as e:
        print(f"Error gathering chat info: {e}")
        chat_infos = [None] * len(channels[start_idx:end_idx])

    text = "<b>➤ Cᴏɴɴᴇᴄᴛᴇᴅ Cʜᴀɴɴᴇʟs (ID & Name):</b>\n\n"
    for i, chat_info in enumerate(chat_infos):
        idx = start_idx + i + 1
        channel_id = channels[start_idx + i]

        if isinstance(chat_info, Exception) or chat_info is None:
            text += f"<b>{idx}. Channel {channel_id}</b> (Error)\n"
            continue

        text += f"<b>{idx}. {chat_info.title}</b> <code>({channel_id})</code>\n"

    text += f"\n<b>📄 Pᴀɢᴇ {page + 1} ᴏғ {total_pages}</b>"

    # Navigation buttons
    buttons = []
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("• Pʀᴇᴠɪᴏᴜs •", callback_data=f"channelids_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("• Nᴇxᴛ •", callback_data=f"channelids_{page+1}"))
    if nav_buttons:
        buttons.append(nav_buttons)

    reply_markup = InlineKeyboardMarkup(buttons) if buttons else None
    if edit:
        await message.edit_text(text, reply_markup=reply_markup)
    else:
        await message.reply(text, reply_markup=reply_markup)

@Client.on_callback_query(filters.regex(r"channelids_(\d+)"))
async def paginate_channel_ids(client: Client, callback_query):
    page = int(callback_query.data.split("_")[1])
    channels = await get_channels()
    await send_channel_ids_page(client, callback_query.message, channels, page, edit=True)

# Helper function to get chat info with caching
async def get_chat_info(client, channel_id):
    # Check cache first
    if channel_id in chat_info_cache:
        cached_info, timestamp = chat_info_cache[channel_id]
        # Cache for 5 minutes
        if (datetime.now() - timestamp).total_seconds() < 300:
            return cached_info

    # Fetch fresh info
    try:
        chat_info = await client.get_chat(channel_id)
        # Cache the result
        chat_info_cache[channel_id] = (chat_info, datetime.now())
        return chat_info
    except Exception as e:
        print(f"Error getting chat info for {channel_id}: {e}")
        # Return cached info even if stale if we can't get fresh info
        if channel_id in chat_info_cache:
            return chat_info_cache[channel_id][0]
        raise e
