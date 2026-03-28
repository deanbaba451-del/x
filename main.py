import os
import asyncio
from flask import Flask
from threading import Thread
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import MediaStream
from yt_dlp import YoutubeDL

# render canli tutma
app_web = Flask(__name__)
@app_web.route('/')
def index(): return "aktif"
def run_web(): app_web.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

# config
API_ID = 38517910
API_HASH = "974a2b5877fab4867b1b48276d9e1c39"
BOT_TOKEN = "8704398105:AAHUDlefwnDrbocCW4P4nrFvBnLDlId7ajA"
SESSION = "1ApWapzMBuw9ze4zqHf0mI9Qcie6Kqt3ACixzOYMJ7AJT4H_wUalzlsMWZAeh4nU4kHCMzqZjNgJ8LH5fxWr9O1_9_uIF0lNkBzM0m4dlOwE8vAZomaOTOUPtz6SdTVg6hsOU3cfIae8HdLYF4zVsocOHUgYiZj3Ao1RVUp2fN9BDanl9EfPbd7M9dWy54nSpU9rcG4GZaDD3xzkPHJHyHEGaWTRiqPzMgCEKlKehB61ZDMZ8glgJatMZEcqHEoNycd9FHuk-9TQZpWqfCLvURsdbQBCemfoEKFG2mPT7tLdrStYbqZ0FeQ3cxh_FVerpTRJg2yGRalCxM6qi-R3-xoS2O01U3LU="
ASISTAN_ID = "+77086222094"
SUDO_USER = 6534222591

auth_users = {SUDO_USER}
tagging_active = []
blacklist = set()

bot = Client("hasret_muzik", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
user = Client("asistan", api_id=API_ID, api_hash=API_HASH, session_string=SESSION)
call = PyTgCalls(user)
ytdl = YoutubeDL({"format": "bestaudio/best", "quiet": True, "noplaylist": True})

def is_auth(uid): return uid in auth_users or uid == SUDO_USER

# tagger
@bot.on_message(filters.command(["utag", "atag", "tag", "etag", "gtag", "davet"]) & filters.group)
async def tagger(c, m):
    if not is_auth(m.from_user.id): return await m.reply("yetkiniz yok")
    chat_id = m.chat.id
    tagging_active.append(chat_id)
    await m.reply("islem baslatildi")
    async for member in c.get_chat_members(chat_id):
        if chat_id not in tagging_active: break
        if member.user.is_bot: continue
        await c.send_message(chat_id, f"{member.user.mention}")
        await asyncio.sleep(2)

@bot.on_message(filters.command("bitir") & filters.group)
async def stop_tag(c, m):
    if not is_auth(m.from_user.id): return
    if m.chat.id in tagging_active:
        tagging_active.remove(m.chat.id)
        await m.reply("islem durduruldu")

# muzik
@bot.on_message(filters.command(["oynat", "voynat"]) & filters.group)
async def play(c, m):
    if len(m.command) < 2: return await m.reply("sarki adi yaz")
    res = await m.reply("hazirlaniyor")
    try: await bot.add_chat_members(m.chat.id, ASISTAN_ID)
    except: pass
    query = m.text.split(None, 1)[1]
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]
        await call.play(m.chat.id, MediaStream(info['formats'][0]['url']))
        await res.edit(f"oynatiliyor: {info['title'].lower()}")
    except Exception as e: await res.edit(f"hata: {str(e).lower()}")

@bot.on_message(filters.command(["son", "dur", "duraklat", "devam", "atla"]))
async def control(c, m):
    if not is_auth(m.from_user.id): return
    cmd = m.command[0]
    try:
        if cmd in ["son", "dur"]: await call.leave_call(m.chat.id)
        await m.reply(f"{cmd} basarili")
    except: pass

@bot.on_message(filters.command("start"))
async def start(c, m):
    await m.reply_text(
        "merhaba hasret muzik aktif yardim icin butona tikla",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("beni gruba ekle", url="https://t.me/hasret_muzik_bot?startgroup=true")],
            [InlineKeyboardButton("destek", url="https://t.me/komtanim")]
        ])
    )

async def boot():
    Thread(target=run_web, daemon=True).start()
    await bot.start()
    await user.start()
    await call.start()
    await asyncio.idle()

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(boot())
