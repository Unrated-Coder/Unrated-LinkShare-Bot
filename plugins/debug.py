from pyrogram import Client, filters
from config import LOGGER

@Client.on_message(filters.all, group=-1)
async def debug_log(client, message):
    if message.text:
        LOGGER(__name__).info(f"MSG from {message.from_user.id if message.from_user else 'unknown'}: {message.text[:50]}")
