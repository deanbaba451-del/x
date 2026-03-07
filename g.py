import os
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

# --- YAPILANDIRMA ---
API_ID = 36856573
API_HASH = "9045fafb55bc4aa6fa2aadafbb1f2e1e"
STRING_SESSION = "1AZWarzcBuzEjXmTrsquzVl8EHfSvgy-GG46gWV0G79-2rlzDK_9kaEcvxRpjdiQJYqezBWpu6GDq_iM3e2v6BhiXApHHGkXTzrjXU1gjuwdUQkp_7YmnDCYhznOhEOLRxa_29L6FmwiN1XxckVbVW0Xtgi0G8s1I7HTK9f_w-LXzAOaDS_4yEyPS0SQ9T2sxaeWfS8cno9F6612lB07vo1xRqZ5SdhxWZQViYHhZNG5P2PI8FwLo5rxqLPPoy10kq0IkuINswQDZLnoOENldmi6k_lr4F8-6RP07Poe6_Cs2ZQbXCOI2nJ7IFh582Or3xxdiBXGdRkyC3egf5Rr6BfpXU35mJFU="
OWNERS = [6534222591, 8256872080]

# Client nesnesini oluşturuyoruz
app = Client(
    "render_userbot",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    in_memory=True  # Render için session dosyasını diskte değil RAM'de tutar
)

PHONE_PATTERN = r"(\+?\d{1,3}[- ]?)?\d{10,12}"

# 1. OTOMATİK: Numara Silme
@app.on_message(filters.group & ~filters.me)
async def auto_handler(_, message):
    if message.text and re.search(PHONE_PATTERN, message.text):
        try:
            await message.delete()
        except: pass

# 2. KOMUT: /pas @hedef (Metin/Ses hariç her şeyi siler)
@app.on_message(filters.command("pas", prefixes="/") & filters.user(OWNERS) & filters.private)
async def delete_media_only(_, message):
    if len(message.command) < 2: return
    target = message.command[1].replace("@", "")
    
    async for msg in app.get_chat_history(target):
        if not (msg.text or msg.voice or msg.audio):
            try:
                await msg.delete()
                await asyncio.sleep(0.1)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except: continue

# 3. KOMUT: /pass @hedef (Her şeyi siler)
@app.on_message(filters.command("pass", prefixes="/") & filters.user(OWNERS))
async def delete_all(_, message):
    if len(message.command) < 2: return
    target = message.command[1].replace("@", "")
    
    async for msg in app.get_chat_history(target):
        try:
            await msg.delete()
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except: continue

# Render ve Python 3.12+ uyumlu başlatıcı
async def main():
    print("Userbot başlatılıyor...")
    await app.start()
    print("Userbot Render üzerinde AKTİF!")
    # Botun kapanmaması için sonsuz döngüde bekletiyoruz
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
