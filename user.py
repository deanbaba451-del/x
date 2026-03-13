import asyncio
import random
import os
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserPrivacyRestricted, UserAlreadyParticipant

# --- BİLGİLERİN ---
API_ID = 36228429
API_HASH = "17a7a801f1c633cfaceefc775833bcd5"
BOT_TOKEN = "8659723253:AAFTF6FlFE-fo98RF9U5h6fnvTC-7OtVYZM"
ANA_SESSION = "AQIozU0AZKLSUnZlxFGSVOclGVyBs2gwssOZ428co23FH2BWVacOI3yBqIOJiwLsdKxRhFFm6rlxyohKnqAPqlrc31T4jF7MxKAfJxpHUALeSx4XOC9JPjZdvW762Ie-1DxRjB6VGRUvuMMO93bwc7tfznnl6TerzR_z2dTInAaRVgmtxIuO_Y1yysb48bwCSbk0k7_9aNIADKjxf9GoE44b7jzIB40d84XMlPIfdEe-BfWhoRLVZKWXk06PKMGAXGkfEDZEZjpelzcOHqUMDlPi8px2z-66ecJrAVjGWdWgJIFxfz9pX7tI_s-g0tm8hsqvq5pmVQYlJHbUsUxRD4DNafiiAgAAAAHzCS3iAA"

# --- BOTLARI HAZIRLA ---
# sync_current_set_loop hatasını önlemek için Client'ı döngü içinde başlatacağız
bot = Client("manager_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, in_memory=True)
ubot = Client("user_account", api_id=API_ID, api_hash=API_HASH, session_string=ANA_SESSION, in_memory=True)

data = {}

@bot.on_message(filters.command("start") & filters.private)
async def start_cmd(c, m):
    await m.reply("🤖 **Bot Aktif!**\n\nGrupların taranıyor, lütfen bekle...")
    buttons = []
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    try:
        async for dialog in ubot.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"src_{dialog.chat.id}")])
        if not buttons:
            return await m.reply("❌ Hiç grup bulunamadı.")
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
        await q.message.edit_text("🚀 **İşlem başladı!** Üyeler ekleniyor...")
        added = 0
        async for member in ubot.get_chat_members(src_id):
            if member.user.is_bot or member.user.is_deleted: continue
            try:
                await ubot.add_chat_members(trg_id, member.user.id)
                added += 1
                if added % 5 == 0: await c.send_message(uid, f"✅ Durum: {added} üye eklendi.")
                await asyncio.sleep(random.randint(30, 60)) # Daha güvenli süre
            except FloodWait as e: await asyncio.sleep(e.value + 15)
            except Exception: continue
        await c.send_message(uid, f"🏁 **Bitti!** Toplam {added} üye.")

async def main():
    print("Botlar uyandırılıyor...")
    await bot.start()
    await ubot.start()
    print("Botlar başarıyla bağlandı!")
    # Render'ın 'No open ports' hatasını engellemek için sonsuz bekleme
    while True:
        await asyncio.sleep(1000)

if __name__ == "__main__":
    asyncio.run(main())
