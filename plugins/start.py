# Bluuuuuuuuuuhh....🥴 Visit our Channel ~ t.me/Unrated_Coder
# Nothing... 
# 😶

import asyncio
import base64
import time
from asyncio import Lock
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.enums import ParseMode, ChatMemberStatus, ChatAction
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram.errors import FloodWait, UserNotParticipant, UserIsBlocked, InputUserDeactivated, MessageNotModified
import os
import asyncio
from asyncio import sleep
from asyncio import Lock
import random 

from datetime import datetime, timedelta
from config import *
from database.database import *
import database.database as db
from plugins.newpost import revoke_invite_after_5_minutes
from helper_func import *

# Create a lock dictionary for each channel to prevent concurrent link generation
channel_locks = defaultdict(asyncio.Lock)

user_banned_until = {}

# Broadcast variables
cancel_lock = asyncio.Lock()
is_canceled = False

@Client.on_message(filters.command('start') & filters.private)
async def start_command(client: Client, message: Message):
    user_id = message.from_user.id

    if user_id in user_banned_until:
        if datetime.now() < user_banned_until[user_id]:
            return await message.reply_text(
                "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
                parse_mode=ParseMode.HTML
            )
            
    await add_user(user_id)

    # Check FSub requirements
    fsub_data = await get_fsub_channels()
    if fsub_data:
        must_join = []

        async def check_fsub(ch):
            channel_id = ch['channel_id']
            mode = ch.get('mode', 'normal')
            try:
                member = await client.get_chat_member(channel_id, user_id)
                if mode == "request" and member.status == ChatMemberStatus.BANNED:
                    return ch
            except UserNotParticipant:
                return ch
            except Exception as e:
                print(f"FSub Check Error for {channel_id}: {e}")
            return None

        results = await asyncio.gather(*[check_fsub(ch) for ch in fsub_data])
        must_join = [res for res in results if res is not None]

        if must_join:
            buttons = []
            for ch in must_join:
                try:
                    fsub_id = ch['channel_id']
                    mode = ch.get('mode', 'normal')
                    chat = await client.get_chat(fsub_id)

                    if mode == "request":
                        # For request mode, we generate a link that creates a join request if not already present
                        link = chat.invite_link or (await client.create_chat_invite_link(fsub_id, creates_join_request=True)).invite_link
                    else:
                        link = chat.invite_link or (await client.export_chat_invite_link(fsub_id))

                    buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=link)])
                except Exception as e:
                    print(f"FSub Button Error: {e}")

            if buttons:
                me = client.me or (await client.get_me())
                start_param = message.command[1] if len(message.command) > 1 else ''
                buttons.append([InlineKeyboardButton("🔄 Check Again", url=f"https://t.me/{me.username}?start={start_param}")])
                return await message.reply_text(
                    "<b>👋 Welcome!\n\nTo use this bot, you must join our channels first. Click the buttons below to join, then click 'Check Again'.</b>",
                    reply_markup=InlineKeyboardMarkup(buttons)
                )

    text = message.text
    if len(text) > 7:
        try:
            base64_string = text.split(" ", 1)[1]
            is_request = base64_string.startswith("req_")
            
            if is_request:
                base64_string = base64_string[4:]
                channel_id = await get_channel_by_encoded_link2(base64_string)
            else:
                channel_id = await get_channel_by_encoded_link(base64_string)
            
            if not channel_id:
                return await message.reply_text(
                    "<b><blockquote expandable>Invalid or expired invite link.</b>",
                    parse_mode=ParseMode.HTML
                )

            # Check if this is a /genlink link (original_link exists)
            from database.database import get_original_link
            original_link = await get_original_link(channel_id)
            if original_link:
                button = InlineKeyboardMarkup(
                    [[InlineKeyboardButton("• Proceed to Link •", url=original_link)]]
                )
                return await message.reply_text(
                    "<b><blockquote expandable>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ</b>",
                    reply_markup=button,
                    parse_mode=ParseMode.HTML
                )

            # Use a lock for this channel to prevent concurrent link generation
            async with channel_locks[channel_id]:
                # Check if we already have a valid link
                old_link_info = await get_current_invite_link(channel_id)
                current_time = datetime.now()
                
                # If we have an existing link and it's not expired yet (assuming 5 minutes validity)
                if old_link_info:
                    link_created_time = await get_link_creation_time(channel_id)
                    if link_created_time and (current_time - link_created_time).total_seconds() < 240:  # 4 minutes
                        # Use existing link
                        invite_link = old_link_info["invite_link"]
                        is_request_link = old_link_info["is_request"]
                    else:
                        # Revoke old link and create new one
                        try:
                            await client.revoke_chat_invite_link(channel_id, old_link_info["invite_link"])
                            print(f"Revoked old {'request' if old_link_info['is_request'] else 'invite'} link for channel {channel_id}")
                        except (InviteHashExpired, RPCError):
                            pass
                        except Exception as e:
                            print(f"Failed to revoke old link for channel {channel_id}: {e}")
                        
                        # Create new link
                        invite = await client.create_chat_invite_link(
                            chat_id=channel_id,
                            expire_date=current_time + timedelta(minutes=10),
                            creates_join_request=is_request
                        )
                        invite_link = invite.invite_link
                        is_request_link = is_request
                        await save_invite_link(channel_id, invite_link, is_request_link)
                else:
                    # Create new link
                    invite = await client.create_chat_invite_link(
                        chat_id=channel_id,
                        expire_date=current_time + timedelta(minutes=10),
                        creates_join_request=is_request
                    )
                    invite_link = invite.invite_link
                    is_request_link = is_request
                    await save_invite_link(channel_id, invite_link, is_request_link)

            button_text = "• ʀᴇǫᴜᴇsᴛ ᴛᴏ ᴊᴏɪɴ •" if is_request_link else "• ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ •"
            button = InlineKeyboardMarkup([[InlineKeyboardButton(button_text, url=invite_link)]])

            await message.reply_text(
                "<b><blockquote expandable>ʜᴇʀᴇ ɪs ʏᴏᴜʀ ʟɪɴᴋ! ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ</b>",
                reply_markup=button,
                parse_mode=ParseMode.HTML
            )

            note_msg = await message.reply_text(
                "<u><b>Note: If the link is expired, please click the post link again to get a new one.</b></u>",
                parse_mode=ParseMode.HTML
            )

            # Auto-delete the note message after 5 minutes
            asyncio.create_task(delete_after_delay(note_msg, 300))

            asyncio.create_task(revoke_invite_after_5_minutes(client, channel_id, invite_link, is_request_link))

        except Exception as e:
            await message.reply_text(
                "<b><blockquote expandable>Invalid or expired invite link.</b>",
                parse_mode=ParseMode.HTML
            )
            print(f"Decoding error: {e}")
    else:
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                 InlineKeyboardButton("ᴄʜᴀɴɴᴇʟs •", callback_data="channels")],
                [InlineKeyboardButton("• Jᴏɪɴ ᴜᴘᴅᴀᴛᴇs •", url="https://t.me/Unrated_Coder")]
            ]
        )
        
        try:
            await message.reply_photo(
                photo=START_PIC,
                caption=START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )
        except Exception as e:
            print(f"Error sending start picture: {e}")
            await message.reply_text(
                START_MSG,
                reply_markup=inline_buttons,
                parse_mode=ParseMode.HTML
            )


async def check_subscription_status(client: Client, user_id: int, fsub_channels: list):
    must_join = []
    for ch in fsub_channels:
        channel_id = ch['channel_id']
        mode = ch.get('mode', 'normal')
        try:
            member = await client.get_chat_member(channel_id, user_id)
            if mode == "request" and member.status == ChatMemberStatus.BANNED:
                must_join.append(ch)
        except UserNotParticipant:
            must_join.append(ch)
        except Exception as e:
            print(f"FSub Check Error for {channel_id}: {e}")
            
    if not must_join:
        return True, "", None
        
    buttons = []
    for ch in must_join:
        try:
            fsub_id = ch['channel_id']
            mode = ch.get('mode', 'normal')
            chat = await client.get_chat(fsub_id)
            if mode == "request":
                link = chat.invite_link or (await client.create_chat_invite_link(fsub_id, creates_join_request=True)).invite_link
            else:
                link = chat.invite_link or (await client.export_chat_invite_link(fsub_id))
            buttons.append([InlineKeyboardButton(f"Join {chat.title}", url=link)])
        except Exception as e:
            print(f"FSub Button Error: {e}")
            
    buttons.append([InlineKeyboardButton("🔄 Check Again", callback_data="check_sub")])
    
    markup = InlineKeyboardMarkup(buttons)
    message_text = "<b>👋 Welcome!\n\nTo use this bot, you must join our channels first. Click the buttons below to join, then click 'Check Again'.</b>"
    return False, message_text, markup


@Client.on_callback_query(filters.regex("close"))
async def close_callback(client: Client, callback_query):
    await callback_query.answer()
    await callback_query.message.delete()

@Client.on_callback_query(filters.regex("check_sub"))
async def check_sub_callback(client: Client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    fsub_channels = await get_fsub_channels()
    
    if not fsub_channels:
        await callback_query.message.edit_text(
            "<b>No FSub channels configured!</b>",
            parse_mode=ParseMode.HTML
        )
        return
    
    is_subscribed, subscription_message, subscription_buttons = await check_subscription_status(client, user_id, fsub_channels)
    if is_subscribed:
        await callback_query.message.edit_text(
            "<b>You are subscribed to all required channels! Use /start to proceed.</b>",
            parse_mode=ParseMode.HTML
        )
    else:
        await callback_query.message.edit_text(
            subscription_message,
            reply_markup=subscription_buttons,
            parse_mode=ParseMode.HTML
        )

WAIT_MSG = "<b>Processing...</b>"

REPLY_ERROR = """Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ Tᴇʟᴇɢʀᴀᴍ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀɴʏ sᴘᴀᴄᴇs."""

@Client.on_message(filters.command('status') & filters.private & is_owner_or_admin)
async def info(client: Client, message: Message):
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("• Close •", callback_data="close")]])
    
    start_time = time.time()
    
    total_users = await count_users()

    end_time = time.time()
    ping_time = (end_time - start_time) * 1000
    
    now = datetime.now()
    delta = now - getattr(client, "uptime", now)
    bottime = get_readable_time(delta.seconds)
    
    await message.reply_text(
        f"<b>Users: {total_users}\n\nUptime: {bottime}\n\nPing: {ping_time:.2f} ms</b>",
        reply_markup=reply_markup,
        parse_mode=ParseMode.HTML
    )

#--------------------------------------------------------------[[ADMIN COMMANDS]]---------------------------------------------------------------------------#
# Handler for the /cancel command
@Client.on_message(filters.command('cancel') & filters.private & is_owner_or_admin)
async def cancel_broadcast(client: Client, message: Message):
    global is_canceled
    async with cancel_lock:
        is_canceled = True

@Client.on_message(filters.private & filters.command('broadcast') & is_owner_or_admin)
async def broadcast(client: Client, message: Message):
    global is_canceled
    args = message.text.split()[1:]

    if not message.reply_to_message:
        msg = await message.reply(
            "Reply to a message to broadcast.\n\nUsage examples:\n"
            "`/broadcast normal`\n"
            "`/broadcast pin`\n"
            "`/broadcast delete 30`\n"
            "`/broadcast pin delete 30`\n"
            "`/broadcast silent`\n"
        )
        await asyncio.sleep(8)
        return await msg.delete()

    # Defaults
    do_pin = False
    do_delete = False
    duration = 0
    silent = False
    mode_text = []

    i = 0
    while i < len(args):
        arg = args[i].lower()
        if arg == "pin":
            do_pin = True
            mode_text.append("PIN")
        elif arg == "delete":
            do_delete = True
            try:
                duration = int(args[i + 1])
                i += 1
            except (IndexError, ValueError):
                return await message.reply("<b>Provide valid duration for delete mode.</b>\nUsage: `/broadcast delete 30`")
            mode_text.append(f"DELETE({duration}s)")
        elif arg == "silent":
            silent = True
            mode_text.append("SILENT")
        else:
            mode_text.append(arg.upper())
        i += 1

    if not mode_text:
        mode_text.append("NORMAL")

    # Reset cancel flag
    async with cancel_lock:
        is_canceled = False

    from database.database import user_data
    total = await count_users()
    broadcast_msg = message.reply_to_message
    successful = blocked = deleted = unsuccessful = 0

    pls_wait = await message.reply(f"<i>Broadcasting in <b>{' + '.join(mode_text)}</b> mode...</i>")

    bar_length = 20
    progress_bar = ''
    last_update_percentage = 0
    update_interval = 0.05  # 5%

    i = 0
    async for user in user_data.find():
        i += 1
        chat_id = user['_id']
        async with cancel_lock:
            if is_canceled:
                await pls_wait.edit(f"›› BROADCAST ({' + '.join(mode_text)}) CANCELED ❌")
                return

        try:
            sent_msg = await broadcast_msg.copy(chat_id, disable_notification=silent)

            if do_pin:
                await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
            if do_delete:
                asyncio.create_task(auto_delete(sent_msg, duration))

            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)
            try:
                sent_msg = await broadcast_msg.copy(chat_id, disable_notification=silent)
                if do_pin:
                    await client.pin_chat_message(chat_id, sent_msg.id, both_sides=True)
                if do_delete:
                    asyncio.create_task(auto_delete(sent_msg, duration))
                successful += 1
            except:
                unsuccessful += 1
        except UserIsBlocked:
            await del_user(chat_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(chat_id)
            deleted += 1
        except:
            unsuccessful += 1
            await del_user(chat_id)

        # Progress
        percent_complete = i / total
        if percent_complete - last_update_percentage >= update_interval or last_update_percentage == 0:
            num_blocks = int(percent_complete * bar_length)
            progress_bar = "●" * num_blocks + "○" * (bar_length - num_blocks)
            status_update = f"""<b>›› BROADCAST ({' + '.join(mode_text)}) IN PROGRESS...

<blockquote>⏳:</b> [{progress_bar}] <code>{percent_complete:.0%}</code></blockquote>

<b>›› Total Users: <code>{total}</code>
›› Successful: <code>{successful}</code>
›› Blocked: <code>{blocked}</code>
›› Deleted: <code>{deleted}</code>
›› Unsuccessful: <code>{unsuccessful}</code></b>

<i>➪ To stop broadcasting click: <b>/cancel</b></i>"""
            await pls_wait.edit(status_update)
            last_update_percentage = percent_complete

    # Final status
    final_status = f"""<b>›› BROADCAST ({' + '.join(mode_text)}) COMPLETED ✅

<blockquote>Dᴏɴᴇ:</b> [{progress_bar}] {percent_complete:.0%}</blockquote>

<b>›› Total Users: <code>{total}</code>
›› Successful: <code>{successful}</code>
›› Blocked: <code>{blocked}</code>
›› Deleted: <code>{deleted}</code>
›› Unsuccessful: <code>{unsuccessful}</code></b>"""
    return await pls_wait.edit(final_status)


# helper for delete mode
async def auto_delete(sent_msg, duration):
    await asyncio.sleep(duration)
    try:
        await sent_msg.delete()
    except:
        pass


#----------------------------------

user_message_count = {}
# user_banned_until = {} # Already defined above

MAX_MESSAGES = 3
TIME_WINDOW = timedelta(seconds=10)
BAN_DURATION = timedelta(hours=1)

"""

@Client.on_message(filters.private)
async def monitor_messages(client: Client, message: Message):
    user_id = message.from_user.id
    now = datetime.now()

    if message.text and message.text.startswith("/"):
        return

    if user_id in ADMINS:
        return 

    if user_id in user_banned_until and now < user_banned_until[user_id]:
        await message.reply_text(
            "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
            parse_mode=ParseMode.HTML
        )
        return

    if user_id not in user_message_count:
        user_message_count[user_id] = []

    user_message_count[user_id].append(now)
    user_message_count[user_id] = [time for time in user_message_count[user_id] if now - time <= TIME_WINDOW]

    if len(user_message_count[user_id]) > MAX_MESSAGES:
        user_banned_until[user_id] = now + BAN_DURATION
        await message.reply_text(
            "<b><blockquote expandable>You are temporarily banned from using commands due to spamming. Try again later.</b>",
            parse_mode=ParseMode.HTML
        )
        return

"""

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    data = query.data  
    chat_id = query.message.chat.id
    
    if data == "close":
        await query.message.delete()
        try:
            await query.message.reply_to_message.delete()
        except:
            pass
    
    elif data == "about":
        try:
            await query.edit_message_media(
                InputMediaPhoto(
                    "https://graph.org/file/7228e9fe7ebf6145cca11-38b598b785ee91950b.jpg",
                    ABOUT_TXT
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('ᴄʟᴏsᴇ •', callback_data='close')]
                ]),
            )
        except MessageNotModified:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴀʙᴏᴜᴛ sᴇᴄᴛɪᴏɴ ❗", show_alert=False)

    elif data == "channels":
        try:
            await query.edit_message_media(
                InputMediaPhoto("https://graph.org/file/7228e9fe7ebf6145cca11-38b598b785ee91950b.jpg", 
                                CHANNELS_TXT
                ),
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton('• ʙᴀᴄᴋ', callback_data='start'), InlineKeyboardButton('ᴄʟᴏsᴇ •', callback_data='close')]
                ]),
            )
        except MessageNotModified:
            await query.answer("ʏᴏᴜ ᴀʀᴇ ᴀʟʀᴇᴀᴅʏ ɪɴ ᴄʜᴀɴɴᴇʟs sᴇᴄᴛɪᴏɴ ❗", show_alert=False)

    elif data in ["start", "home"]:
        inline_buttons = InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("• ᴀʙᴏᴜᴛ", callback_data="about"),
                 InlineKeyboardButton("ᴄʜᴀɴɴᴇʟs •", callback_data="channels")],
                [InlineKeyboardButton("• Jᴏɪɴ ᴜᴘᴅᴀᴛᴇs •", url="https://t.me/Unrated_Coder")]
            ]
        )
        try:
            await query.edit_message_media(
                InputMediaPhoto(
                    START_PIC,
                    START_MSG
                ),
                reply_markup=inline_buttons
            )
        except MessageNotModified:
            await query.answer("ʜᴏᴍᴇ ᴘᴀɢᴇ ᴀʟʀᴇᴀᴅʏ ᴏᴘᴇɴ ❗", show_alert=False)
        except Exception as e:
            print(f"Error sending start/home photo: {e}")
            try:
                await query.edit_message_text(
                    START_MSG,
                    reply_markup=inline_buttons,
                    parse_mode=ParseMode.HTML
                )
            except MessageNotModified:
                pass


    elif data.startswith("rfs_ch_"):
        cid = int(data.split("_")[2])
        try:
            chat = await client.get_chat(cid)
            mode = await db.get_channel_mode(cid)
            status = "🟢 ᴏɴ" if mode == "on" else "🔴 ᴏғғ"
            new_mode = "off" if mode == "on" else "on"
            buttons = [
                [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
                [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
            ]
            await query.message.edit_text(
                f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
        except Exception:
            await query.answer("Failed to fetch channel info", show_alert=True)

    elif data.startswith("rfs_toggle_"):
        cid, action = data.split("_")[2:]
        cid = int(cid)
        mode = "on" if action == "on" else "off"

        await db.set_channel_mode(cid, mode)
        await query.answer(f"Force-Sub set to {'ON' if mode == 'on' else 'OFF'}")

        # Refresh the same channel's mode view
        chat = await client.get_chat(cid)
        status = "🟢 ON" if mode == "on" else "🔴 OFF"
        new_mode = "off" if mode == "on" else "on"
        buttons = [
            [InlineKeyboardButton(f"ʀᴇǫ ᴍᴏᴅᴇ {'OFF' if mode == 'on' else 'ON'}", callback_data=f"rfs_toggle_{cid}_{new_mode}")],
            [InlineKeyboardButton("‹ ʙᴀᴄᴋ", callback_data="fsub_back")]
        ]
        await query.message.edit_text(
            f"Channel: {chat.title}\nCurrent Force-Sub Mode: {status}",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    elif data == "fsub_back":
        channels = await db.show_channels()
        buttons = []
        for cid in channels:
            try:
                chat = await client.get_chat(cid)
                mode = await db.get_channel_mode(cid)
                status = "🟢" if mode == "on" else "🔴"
                buttons.append([InlineKeyboardButton(f"{status} {chat.title}", callback_data=f"rfs_ch_{cid}")])
            except:
                continue

        await query.message.edit_text(
            "sᴇʟᴇᴄᴛ ᴀ ᴄʜᴀɴɴᴇʟ ᴛᴏ ᴛᴏɢɢʟᴇ ɪᴛs ғᴏʀᴄᴇ-sᴜʙ ᴍᴏᴅᴇ:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

def delete_after_delay(msg, delay):
    async def inner():
        await asyncio.sleep(delay)
        try:
            await msg.delete()
        except:
            pass
    return inner()
