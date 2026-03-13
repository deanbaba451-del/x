import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Loglama (Render panelinde hataları görmek için)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# YENİ TOKEN
TOKEN = "8445071969:AAFjTl-k6tidEDTCvF6IIvr7BMnkML1cq5Q"

async def delete_warning(context, chat_id, message_id):
    """Uyarı mesajını 60 saniye sonra siler."""
    await asyncio.sleep(60)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except:
        pass

async def handle_edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Editlenen mesajı yakala
    msg = update.edited_message
    
    # --- HASSASİYET FİLTRELERİ ---
    # 1. Mesaj objesi yoksa veya metin içermiyorsa (sadece tepki/emoji ise) DUR.
    if not msg or not msg.text:
        return

    # 2. Eğer mesajın düzenlenme tarihi yoksa bu teknik olarak bir 'edit' değildir, DUR.
    if not msg.edit_date:
        return

    # 3. Mesajın editlenme zamanı ile gönderilme zamanı aynıysa (bazı tepki bugları için) DUR.
    if msg.date == msg.edit_date:
        return
    # ----------------------------

    user = msg.from_user
    chat_id = msg.chat_id

    try:
        # Editlenen mesajı sil
        await msg.delete()

        # Mention at ve uyarı gönder
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        text = f"{mention}, your edited message has been deleted."
        
        sent_msg = await context.bot.send_message(
            chat_id=chat_id, 
            text=text, 
            parse_mode='HTML'
        )

        # 60 saniye sonra uyarıyı silmek için görev başlat
        asyncio.create_task(delete_warning(context, chat_id, sent_msg.message_id))

    except Exception as e:
        logging.error(f"Hata: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()

    # Filtre: Sadece editlenmiş ve metin içeren mesajlar
    edit_filter = filters.UpdateType.EDITED_MESSAGE & filters.TEXT
    application.add_handler(MessageHandler(edit_filter, handle_edit))

    print("Bot aktif! Tepkileri görmezden gelir, editleri siler.")
    application.run_polling()
