import os
import re
import asyncio

# Python 3.14+ Event Loop Yaması
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

from hydrogram import Client, filters, enums
from hydrogram.errors import FloodWait

# --- AYARLAR ---
API_ID = 36856573
API_HASH = "9045fafb55bc4aa6fa2aadafbb1f2e1e"
STRING_SESSION = "1AZWarzcBuzEjXmTrsquzVl8EHfSvgy-GG46gWV0G79-2rlzDK_9kaEcvxRpjdiQJYqezBWpu6GDq_iM3e2v6BhiXApHHGkXTzrjXU1gjuwdUQkp_7YmnDCYhznOhEOLRxa_29L6FmwiN1XxckVbVW0Xtgi0G8s1I7HTK9f_w-LXzAOaDS_4yEyPS0SQ9T2sxaeWfS8cno9F6612lB07vo1xRqZ5SdhxWZQViYHhZNG5P2PI8FwLo5rxqLPPoy10kq0IkuINswQDZLnoOENldmi6k_lr4F8-6RP07Poe6_Cs2ZQbXCOI2nJ7IFh582Or3xxdiBXGdRkyC3egf5Rr6BfpXU35mJFU="

# YETKİLİ KULLANICILAR (Sadece bu ID'ler komut çalıştırabilir)
OWNERS = [6534222591, 8256872080, 8343507331]

app = Client(
    "render_userbot",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH,
    sleep_threshold=60
)

PHONE_PATTERN = r"(\+?\d{1,3}[- ]?)?\d{10,12}"

# 1. OTOMATİK: Numara Silme (YETKİSİZLER İÇİN)
# Eğer mesaj atan kişi OWNER listesinde DEĞİLSE numarayı siler.
@app.on_message(filters.group & ~filters.user(OWNERS))
async def phone_cleaner(_, message):
    if message.text and re.search(PHONE_PATTERN, message.text):
        try:
            await message.delete()
        except: pass

# 2. KOMUT: /doedaseks (Sadece Yetkililer)
@app.on_message(filters.command("doedaseks", prefixes="/") & filters.user(OWNERS))
async def delete_everything(_, message):
    chat_id = message.chat.id
    try:
        await message.delete() # Komutun kendisini sil
        async for msg in app.get_chat_history(chat_id):
            try:
                await msg.delete()
                await asyncio.sleep(0.2)
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except: continue
    except: pass

# 3. KOMUT: /gayeda (Sadece Yetkililer)
@app.on_message(filters.command("gayeda", prefixes="/") & filters.user(OWNERS))
async def delete_media_only(_, message):
    chat_id = message.chat.id
    try:
        await message.delete() # Komutun kendisini sil
        async for msg in app.get_chat_history(chat_id):
            # Metin ve Ses mesajı DEĞİLSE sil
            if not (msg.text or msg.voice or msg.audio):
                try:
                    await msg.delete()
                    await asyncio.sleep(0.2)
                except FloodWait as e:
                    await asyncio.sleep(e.value)
                except: continue
    except: pass

async def main():
    print("Userbot AKTİF! Sadece yetkili ID'ler komut kullanabilir.")
    await app.start()
    await asyncio.Event().wait()

if __name__ == "__main__":
    loop.run_until_complete(main())
