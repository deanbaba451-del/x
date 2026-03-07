import os
import re
import asyncio
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

# --- YAPILANDIRMA ---
API_ID = 36856573
API_HASH = "9045fafb55bc4aa6fa2aadafbb1f2e1e"
STRING_SESSION = "1AZWarzcBuzEjXmTrsquzVl8EHfSvgy-GG46gWV0G79-2rlzDK_9kaEcvxRpjdiQJYqezBWpu6GDq_iM3e2v6BhiXApHHGkXTzrjXU1gjuwdUQkp_7YmnDCYhznOhEOLRxa_29L6FmwiN1XxckVbVW0Xtgi0G8s1I7HTK9f_w-LXzAOaDS_4yEyPS0SQ9T2sxaeWfS8cno9F6612lB07vo1xRqZ5SdhxWZQViYHhZNG5P2PI8FwLo5rxqLPPoy10kq0IkuINswQDZLnoOENldmi6k_lr4F8-6RP07Poe6_Cs2ZQbXCOI2nJ7IFh582Or3xxdiBXGdRkyC3egf5Rr6BfpXU35mJFU="

# Her iki yönetici ID'si
OWNERS = [6534222591, 8256872080]

app = Client(
    "render_userbot",
    session_string=STRING_SESSION,
    api_id=API_ID,
    api_hash=API_HASH
)

# Numara tespit regexi
PHONE_PATTERN = r"(\+?\d{1,3}[- ]?)?\d{10,12}"

# 1. OTOMATİK: Numara Silme & Hızlı Ban Koruması
@app.on_message(filters.group & ~filters.me)
async def auto_handler(client, message):
    # Numara atılırsa sessizce siler
    if message.text and re.search(PHONE_PATTERN, message.text):
        try:
            await message.delete()
        except: pass

    # Hızlı ban/yetki işlemi yapan botları durdurma mantığı
    if message.service == enums.MessageServiceType.CHAT_MEMBER_LEFT:
        # Burada saniyede 5-10 ban atan bir bot/hesap fark edilirse müdahale edilebilir
        # Şimdilik sessiz izleme modundadır.
        pass

# 2. KOMUT: /pas @hedef (Sadece Metin ve Ses kalır, gerisi silinir)
@app.on_message(filters.command("pas", prefixes="/") & filters.user(OWNERS))
async def delete_media_only(client, message):
    if len(message.command) < 2: return
    target = message.command[1].replace("@", "")
    
    async for msg in client.get_chat_history(target):
        if not (msg.text or msg.voice or msg.audio):
            try:
                await msg.delete()
                await asyncio.sleep(0.1) # Hız sınırı (Flood) yememek için
            except FloodWait as e:
                await asyncio.sleep(e.value)
            except: continue

# 3. KOMUT: /pass @hedef (Gruptaki/Sohbetteki HER ŞEYİ siler)
@app.on_message(filters.command("pass", prefixes="/") & filters.user(OWNERS))
async def delete_all(client, message):
    if len(message.command) < 2: return
    target = message.command[1].replace("@", "")
    
    async for msg in client.get_chat_history(target):
        try:
            await msg.delete()
            await asyncio.sleep(0.1)
        except FloodWait as e:
            await asyncio.sleep(e.value)
        except: continue

print("Userbot Render üzerinde 7/24 aktif!")
app.run()
