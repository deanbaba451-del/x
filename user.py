import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Render loglarını takip etmek için
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8445071969:AAGyGSMkm_FR4T041RVokhVZDxS5ciyw6Dg"

async def deleted_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Editlenen mesaj objesini al
    message = update.edited_message
    
    # EĞER: Mesaj içeriği yoksa (sadece emoji/tepki gelmişse) işlemi durdur
    if not message or not message.text:
        return

    # EĞER: Mesajın düzenlenme zamanı yoksa (bazı tepkilerde tetiklenmemesi için güvenlik)
    if not message.edit_date:
        return

    user = message.from_user
    chat_id = message.chat_id
    
    try:
        # 1. Editlenen mesajı sil
        await message.delete()
        
        # 2. Kullanıcıyı mention atarak uyar
        mention = user.mention_html()
        warning_text = f"{mention}, your edited message has been deleted."
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=warning_text,
            parse_mode='HTML'
        )
        logging.info(f"Başarılı: {user.full_name} kullanıcısının editi silindi.")
        
    except Exception as e:
        logging.error(f"Mesaj silinirken hata: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Filters.UpdateType.EDITED_MESSAGE kullanarak sadece düzenlenen mesajları yakalıyoruz
    # filters.TEXT ekleyerek tepki (reaction) güncellemelerini büyük oranda eliyoruz
    edit_handler = MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, deleted_edited_message)
    
    application.add_handler(edit_handler)
    
    print("Bot Render üzerinde çalışmaya hazır...")
    application.run_polling()
