import logging
import logging.config

# Load logging config
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("imdbpy").setLevel(logging.ERROR)

from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from database.ia_filterdb import Media  # Import AFTER instance and Media are properly defined
from database.users_chats_db import db
from info import SESSION, API_ID, API_HASH, BOT_TOKEN, LOG_CHANNEL
from utils import temp
from pyrogram import types
from aiohttp import web
from plugins import web_server
from datetime import date, datetime 
import pytz

PORT = 8080  # as integer

class Bot(Client):
    def __init__(self):
        super().__init__(
            name=SESSION,
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=700,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users, b_chats = await db.get_banned()
        temp.BANNED_USERS = b_users
        temp.BANNED_CHATS = b_chats

        await super().start()

        # Ensure indexes AFTER umongo instance is ready and Media class is fully defined
        await Media.ensure_indexes()

        me = await self.get_me()
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username

        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        current_time = now.strftime("%I:%M:%S %p")

        await self.send_message(
            chat_id=LOG_CHANNEL,
            text=(
                f"@{me.username} Rᴇsᴛᴀʀᴛᴇᴅ !\n\n"
                f"📅 Dᴀᴛᴇ : {today}\n"
                f"⏰ Tɪᴍᴇ : {current_time}\n"
                f"🌐 Tɪᴍᴇᴢᴏɴᴇ : Asia/Kolkata"
            )
        )

        # Start aiohttp web server
        app_runner = web.AppRunner(await web_server())
        await app_runner.setup()
        bind_address = "0.0.0.0"
        await web.TCPSite(app_runner, bind_address, PORT).start()

        logging.info(
            f"{me.first_name} with for Pyrogram v{__version__} (Layer {layer}) started on {me.username}."
        )

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped. Bye.")

app = Bot()
app.run()
