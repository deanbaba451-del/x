import os
import asyncio
from flask import Flask
from threading import Thread
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import EditBannedRequest
from telethon.tl.types import ChatBannedRights

# Flask (Render Port Hatası İçin)
app = Flask(__name__)
@app.route('/')
def index():
    return "hasretsex"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# Telegram Bot
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
STRING_SESSION = os.environ.get("STRING_SESSION")

client = TelegramClient(StringSession(STRING_SESSION), API_ID, API_HASH)
is_active = False
BANNED = ChatBannedRights(until_date=None, view_messages=True)

async def ban_user(chat_id, user_id):
    try:
        await client(EditBannedRequest(chat_id, user_id, BANNED))
    except:
        pass

@client.on(events.NewMessage(pattern=r"^\.on$"))
async def turn_on(e):
    global is_active
    is_active = True
    await e.delete()

@client.on(events.NewMessage(pattern=r"^\.off$"))
async def turn_off(e):
    global is_active
    is_active = False
    await e.delete()

@client.on(events.ChatAction)
async def guard_engine(event):
    if not is_active:
        return
    if event.user_added or event.user_joined:
        target = await event.get_user()
        if target and target.bot:
            chat = event.chat_id
            try:
                adder = await event.get_added_by()
            except:
                adder = None
            await ban_user(chat, target.id)
            if adder:
                await ban_user(chat, adder.id)
                await client.send_message(chat, "hasret fucks your mother.")

def start_bot():
    print("hasretsex")
    client.start()
    client.run_until_disconnected()

if __name__ == "__main__":
    # Flask'ı ayrı bir kanalda başlat (Render uyum)
    Thread(target=run_flask).start()
    # Botu ana kanalda başlat
    start_bot()
