# Upgraded by @Unrated_Coder from Telegram
import asyncio
import sys
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ParseMode
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, PORT, OWNER_ID
from webserver import web_server
from aiohttp import web

name = """
Links Sharing Started
"""

class Bot(Client):
    def __init__(self):
        super().__init__(
            name="Bot",
            api_hash=API_HASH,
            api_id=APP_ID,
            plugins={"root": "plugins"},
            workers=TG_BOT_WORKERS,
            bot_token=TG_BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self, *args, **kwargs):
        if not TG_BOT_TOKEN or not API_HASH or not APP_ID:
            self.LOGGER(__name__).critical("TG_BOT_TOKEN, API_HASH or APP_ID is missing!")
            sys.exit(1)

        # Web-response (Start before bot to satisfy health checks)
        try:
            app = web.AppRunner(await web_server())
            await app.setup()
            bind_address = "0.0.0.0"
            await web.TCPSite(app, bind_address, int(PORT)).start()
            self.LOGGER(__name__).info(f"Web server started on {bind_address}:{PORT}")
        except Exception as e:
            self.LOGGER(__name__).error(f"Failed to start web server on port {PORT}: {e}")

        await super().start()
        usr_bot_me = await self.get_me()
        self.uptime = datetime.now()
        self.username = usr_bot_me.username

        # Notify owner of bot restart
        if OWNER_ID:
            try:
                await asyncio.sleep(2)
                await self.send_message(
                    chat_id=OWNER_ID,
                    text=f"<b><blockquote>🤖 Bot Restarted ♻️\n\nStarted as @{self.username}</blockquote></b>",
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                self.LOGGER(__name__).warning(f"Failed to notify owner ({OWNER_ID}) of bot start: {e}")

        self.set_parse_mode(ParseMode.HTML)
        self.LOGGER(__name__).info(f"Bot Started as @{self.username}")
        self.LOGGER(__name__).info("Bot Running..!")


    async def stop(self, *args):
        await super().stop()
        self.LOGGER(__name__).info("Bot stopped.")

# Global cancel flag for broadcast
is_canceled = False
cancel_lock = asyncio.Lock()

if __name__ == "__main__":
    Bot().run()
