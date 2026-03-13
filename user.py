import asyncio
import sys

# DİKKAT: Pyrogram'ın hata veren sync modülünü henüz yüklenmeden kandırıyoruz
import types
mock_sync = types.ModuleType("pyrogram.sync")
sys.modules["pyrogram.sync"] = mock_sync

import pyrogram
from pyrogram import Client, filters, enums
import random

# --- BİLGİLERİN ---
API_ID = 36228429
API_HASH = "17a7a801f1c633cfaceefc775833bcd5"
BOT_TOKEN = "8659723253:AAFTF6FlFE-fo98RF9U5h6fnvTC-7OtVYZM"
ANA_SESSION = "AQIozU0AZKLSUnZlxFGSVOclGVyBs2gwssOZ428co23FH2BWVacOI3yBqIOJiwLsdKxRhFFm6rlxyohKnqAPqlrc31T4jF7MxKAfJxpHUALeSx4XOC9JPjZdvW762Ie-1DxRjB6VGRUvuMMO93bwc7tfznnl6TerzR_z2dTInAaRVgmtxIuO_Y1yysb48bwCSbk0k7_9aNIADKjxf9GoE44b7jzIB40d84XMlPIfdEe-BfWhoRLVZKWXk06PKMGAXGkfEDZEZjpelzcOHqUMDlPi8px2z-66ecJrAVjGWdWgJIFxfz9pX7tI_s-g0tm8hsqvq5pmVQYlJHbUsUxRD4DNafiiAgAAAAHzCS3iAA"

# Clientları oluştur (Daha başlatmadık)
bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
ubot = Client("user_account", api_id=API_ID, api_hash=API_HASH, session_string=ANA_SESSION, in_memory=True)

data = {}

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(c, m):
    await m.reply("🤖 **Bot Python 3.14 üzerinde uyandı!**\n\nGruplar taranıyor...")
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
        # Buraya önceki ekleme mantığını ekleyebilirsin, temel yapı bu.
        await q.message.edit_text("🚀 İşlem başlatılıyor...")

async def main():
    print(">>> Botlar bağlanıyor...")
    await bot.start()
    await ubot.start()
    print(">>> SİSTEM AKTİF! Telegram'dan /start yazabilirsin.")
    # Botun açık kalmasını sağlayan döngü
    while True:
        await asyncio.sleep(3600)

if __name__ == "__main__":
    # Python 3.14 için en temiz döngü başlatma
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
