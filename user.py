import asyncio
import random
import sys

# Pyrogram'ın hata veren senkron modülünü yamalıyoruz
import pyrogram
pyrogram.sync = None 

from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait

# --- BİLGİLERİN ---
API_ID = 36228429
API_HASH = "17a7a801f1c633cfaceefc775833bcd5"
BOT_TOKEN = "8659723253:AAFTF6FlFE-fo98RF9U5h6fnvTC-7OtVYZM"
ANA_SESSION = "AQIozU0AZKLSUnZlxFGSVOclGVyBs2gwssOZ428co23FH2BWVacOI3yBqIOJiwLsdKxRhFFm6rlxyohKnqAPqlrc31T4jF7MxKAfJxpHUALeSx4XOC9JPjZdvW762Ie-1DxRjB6VGRUvuMMO93bwc7tfznnl6TerzR_z2dTInAaRVgmtxIuO_Y1yysb48bwCSbk0k7_9aNIADKjxf9GoE44b7jzIB40d84XMlPIfdEe-BfWhoRLVZKWXk06PKMGAXGkfEDZEZjpelzcOHqUMDlPi8px2z-66ecJrAVjGWdWgJIFxfz9pX7tI_s-g0tm8hsqvq5pmVQYlJHbUsUxRD4DNafiiAgAAAAHzCS3iAA"

# Client'ları global tanımlıyoruz ama döngü içinde başlatacağız
bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
ubot = Client("user_account", api_id=API_ID, api_hash=API_HASH, session_string=ANA_SESSION)

data = {}

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(c, m):
    await m.reply("🤖 **Bot Aktif!**\n\nGrupların taranıyor...")
    buttons = []
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    try:
        async for dialog in ubot.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"src_{dialog.chat.id}")])
        if not buttons:
            return await m.reply("❌ Grup bulunamadı.")
        await m.reply("📥 **KAYNAK grubu seç:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))
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
        await q.message.edit_text("📤 **HEDEF grubu seç:**", reply_markup=InlineKeyboardMarkup(buttons[:20]))
    elif q.data.startswith("trg_"):
        trg_id = int(q.data.split("_")[1])
        src_id = data[uid]["src_id"]
        await q.message.edit_text("🚀 **İşlem başladı...**")
        added = 0
        async for member in ubot.get_chat_members(src_id):
            if member.user.is_bot or member.user.is_deleted: continue
            try:
                await ubot.add_chat_members(trg_id, member.user.id)
                added += 1
                if added % 5 == 0: await c.send_message(uid, f"✅ Durum: {added} eklendi.")
                await asyncio.sleep(random.randint(30, 60))
            except FloodWait as e: await asyncio.sleep(e.value + 10)
            except Exception: continue
        await c.send_message(uid, f"🏁 Bitti: {added}")

async def run_bot():
    print("Sistem uyandırılıyor...")
    await bot.start()
    await ubot.start()
    print(">>> BOTLAR AKTİF VE BAĞLI! <<<")
    # Render'da açık kalması için sonsuz bekleyiş
    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        await bot.stop()
        await ubot.stop()

if __name__ == "__main__":
    # Python 3.11+ ve 3.14 için en sağlam döngü başlatma yöntemi
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_bot())
