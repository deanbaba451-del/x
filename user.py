import asyncio
import sys
import random

# --- PYROGRAM'I 3.14 UYUMLU HALE GETİRMEK İÇİN YAMA ---
import pyrogram.sync
# Eğer idle yoksa, kütüphane çökmesin diye boş bir fonksiyon atıyoruz
if not hasattr(pyrogram.sync, 'idle'):
    pyrogram.sync.idle = lambda: asyncio.sleep(0)
# ---------------------------------------------------

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

# --- BİLGİLERİN ---
API_ID = 36228429
API_HASH = "17a7a801f1c633cfaceefc775833bcd5"
BOT_TOKEN = "8659723253:AAFTF6FlFE-fo98RF9U5h6fnvTC-7OtVYZM"
ANA_SESSION = "AQIozU0AZKLSUnZlxFGSVOclGVyBs2gwssOZ428co23FH2BWVacOI3yBqIOJiwLsdKxRhFFm6rlxyohKnqAPqlrc31T4jF7MxKAfJxpHUALeSx4XOC9JPjZdvW762Ie-1DxRjB6VGRUvuMMO93bwc7tfznnl6TerzR_z2dTInAaRVgmtxIuO_Y1yysb48bwCSbk0k7_9aNIADKjxf9GoE44b7jzIB40d84XMlPIfdEe-BfWhoRLVZKWXk06PKMGAXGkfEDZEZjpelzcOHqUMDlPi8px2z-66ecJrAVjGWdWgJIFxfz9pX7tI_s-g0tm8hsqvq5pmVQYlJHbUsUxRD4DNafiiAgAAAAHzCS3iAA"

# Client'ları bellekte (in-memory) başlat
bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
ubot = Client("user_account", api_id=API_ID, api_hash=API_HASH, session_string=ANA_SESSION, in_memory=True)

data = {}

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(c, m):
    await m.reply("🤖 **Sistem Başlatıldı!**\n\nGruplar listeleniyor, lütfen bekle...")
    buttons = []
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    try:
        async for dialog in ubot.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"src_{dialog.chat.id}")])
        if not buttons:
            return await m.reply("❌ Grup bulunamadı.")
        await m.reply("📥 **KAYNAK** grubu seç:", reply_markup=InlineKeyboardMarkup(buttons[:20]))
    except Exception as e:
        await m.reply(f"Hata: {e}")

@bot.on_callback_query()
async def callbacks(c, q):
    uid = q.from_user.id
    if q.data.startswith("src_"):
        data[uid] = {"src_id": int(q.data.split("_")[1])}
        buttons = []
        async for dialog in ubot.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"trg_{dialog.chat.id}")])
        await q.message.edit_text("📤 **HEDEF** grubu seç:", reply_markup=InlineKeyboardMarkup(buttons[:20]))
    elif q.data.startswith("trg_"):
        await q.message.edit_text("🚀 Üyeler aktarılıyor...")

async def main():
    print(">>> Servisler ayağa kaldırılıyor...")
    await bot.start()
    await ubot.start()
    print(">>> BOTLAR BAĞLANDI! Telegram'a geçebilirsin.")
    # Render'ın botu durdurmaması için uyanık tutan döngü
    while True:
        await asyncio.sleep(10)

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
