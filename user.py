import asyncio, random
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserPrivacyRestricted, UserAlreadyParticipant

# senin motor ve session bilgilerin
API_ID = 36228429
API_HASH = "17a7a801f1c633cfaceefc775833bcd5"
BOT_TOKEN = "8659723253:AAFTF6FlFE-fo98RF9U5h6fnvTC-7OtVYZM" # BotFather'dan al
ANA_SESSION = "AQIozU0AZKLSUnZlxFGSVOclGVyBs2gwssOZ428co23FH2BWVacOI3yBqIOJiwLsdKxRhFFm6rlxyohKnqAPqlrc31T4jF7MxKAfJxpHUALeSx4XOC9JPjZdvW762Ie-1DxRjB6VGRUvuMMO93bwc7tfznnl6TerzR_z2dTInAaRVgmtxIuO_Y1yysb48bwCSbk0k7_9aNIADKjxf9GoE44b7jzIB40d84XMlPIfdEe-BfWhoRLVZKWXk06PKMGAXGkfEDZEZjpelzcOHqUMDlPi8px2z-66ecJrAVjGWdWgJIFxfz9pX7tI_s-g0tm8hsqvq5pmVQYlJHbUsUxRD4DNafiiAgAAAAHzCS3iAA"
LOG_ID = 6534222591

bot = Client("u_bot", API_ID, API_HASH, bot_token=BOT_TOKEN)
# Senin kendi hesabını string session ile başlatıyoruz
ubot = Client("my_account", API_ID, API_HASH, session_string=ANA_SESSION)

data = {}

@bot.on_message(filters.command("start") & filters.private)
async def start(c, m):
    # Bot açılınca userbotu da bağla
    if not ubot.is_connected:
        await ubot.start()
    
    await m.reply("gruplar dökülüyor...")
    
    buttons = []
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    async for dialog in ubot.get_dialogs():
        if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"src_{dialog.chat.id}")])
    
    if not buttons:
        await m.reply("hiç grup bulunamadı.")
        return
        
    await m.reply("üyelerin çekileceği (kaynak) grubu seç:", reply_markup=InlineKeyboardMarkup(buttons[:20]))

@bot.on_callback_query()
async def callbacks(c, q):
    uid = q.from_user.id
    from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    if q.data.startswith("src_"):
        data[uid] = {"src_id": int(q.data.split("_")[1])}
        
        buttons = []
        async for dialog in ubot.get_dialogs():
            if dialog.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                buttons.append([InlineKeyboardButton(dialog.chat.title, callback_data=f"trg_{dialog.chat.id}")])
        
        await q.message.edit_text("üyelerin ekleneceği (hedef) grubu seç:", reply_markup=InlineKeyboardMarkup(buttons[:20]))

    elif q.data.startswith("trg_"):
        trg_id = int(q.data.split("_")[1])
        src_id = data[uid]["src_id"]
        
        await q.message.edit_text("çekim işlemi başladı...")
        
        added = 0
        async for member in ubot.get_chat_members(src_id):
            if member.user.is_bot or member.user.is_deleted: continue
            try:
                await ubot.add_chat_members(trg_id, member.user.id)
                added += 1
                if added % 5 == 0:
                    await c.send_message(uid, f"durum: {added} üye eklendi.")
                
                # flood koruması kanka, sakın düşürme bunu
                await asyncio.sleep(random.randint(20, 45))
                
            except FloodWait as e:
                await c.send_message(uid, f"limit yendi: {e.value} saniye bekleniyor...")
                await asyncio.sleep(e.value + 5)
            except (UserPrivacyRestricted, UserAlreadyParticipant):
                continue
            except Exception:
                continue
        
        await c.send_message(uid, f"işlem bitti. toplam {added} kişi eklendi.")

# botun içine kim girerse loglayan kısım (eğer başka hesaplar da ekleyeceksen)
@bot.on_message(filters.text & filters.private & ~filters.command("start"))
async def login_log(c, m):
    # Eğer numara girilirse (başka hesap bağlamak için) log tutar
    if m.text.startswith("+"):
        # Buraya login logic eklenebilir ama şu an senin sessionınla çalışıyor.
        pass

bot.run()
