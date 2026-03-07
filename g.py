import os, re, asyncio, sys
from pyrogram import Client, filters
from pyrogram.errors import FloodWait

# Python 3.14 Loop Fix
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

API_ID = 36856573
API_HASH = "9045fafb55bc4aa6fa2aadafbb1f2e1e"
# BURAYA COLAB'DAN ALDIĞIN YENİ VE SAĞLAM STRING'I YAPIŞTIR
STRING_SESSION = "YENI_ALINAN_STRING_BURAYA"

OWNERS = [6534222591, 8256872080, 8343507331]
app = Client("my_bot", session_string=STRING_SESSION, api_id=API_ID, api_hash=API_HASH, in_memory=True)

@app.on_message(filters.group & ~filters.user(OWNERS))
async def auto_del(_, msg):
    if msg.text and re.search(r"(\+?\d{1,3}[- ]?)?\d{10,12}", msg.text):
        try: await msg.delete()
        except: pass

@app.on_message(filters.command("doedaseks", "/") & filters.user(OWNERS))
async def full_clean(_, msg):
    await msg.delete()
    async for m in app.get_chat_history(msg.chat.id):
        try: 
            await m.delete()
            await asyncio.sleep(0.2)
        except FloodWait as e: await asyncio.sleep(e.value)
        except: continue

@app.on_message(filters.command("gayeda", "/") & filters.user(OWNERS))
async def media_clean(_, msg):
    await msg.delete()
    async for m in app.get_chat_history(msg.chat.id):
        if not (m.text or m.voice or m.audio):
            try: 
                await m.delete()
                await asyncio.sleep(0.2)
            except FloodWait as e: await asyncio.sleep(e.value)
            except: continue

@app.on_message(filters.command("durdu", "/") & filters.user(OWNERS))
async def stop_bot(_, msg):
    await msg.delete()
    await app.stop()
    os._exit(0)

async def start_bot():
    print("Bot başlatılıyor...")
    await app.start()
    print("Userbot AKTİF!")
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(start_bot())
