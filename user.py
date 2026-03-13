import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8445071969:AAGyGSMkm_FR4T041RVokhVZDxS5ciyw6Dg"

async def deleted_edited_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Editlenen mesaj objesini al
    message = update.edited_message
    
    # 1. KONTROL: Eğer mesaj objesi boşsa veya metin içermiyorsa (örneğin sadece emoji tepkisiyse) DUR.
    if not message or not message.text:
        return

    # 2. KONTROL: Mesajın ilk yazılma zamanı ile editlenme zamanı aynı mı? 
    # Tepki bırakıldığında bazen bu değerler manipüle olabiliyor.
    # Ayrıca edit_date yoksa bu gerçek bir edit değildir.
    if not message.edit_date:
        return

    # 3. KONTROL: Sadece metin mesajlarını hedef al (Medya altı yazılarını korumak istersen burası önemli)
    # Eğer tepki bırakılıyorsa Telegram genellikle 'text' alanında bir değişiklik yapmaz.
    
    user = message.from_user
    chat_id = message.chat_id
    
    try:
        # Mesajı sil
        await message.delete()
        
        # Kullanıcıya mention at
        mention = f'<a href="tg://user?id={user.id}">{user.first_name}</a>'
        warning_text = f"{mention}, your edited message has been deleted."
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=warning_text,
            parse_mode='HTML'
        )
        logging.info(f"Edit silindi: {user.id}")
        
    except Exception as e:
        logging.error(f"Hata: {e}")

if __name__ == '__main__':
    application = ApplicationBuilder().token(TOKEN).build()
    
    # filters.UpdateType.EDITED_MESSAGE -> Sadece editleri yakalar
    # filters.TEXT -> İçinde metin olanları yakalar (Tepkileri eler)
    edit_handler = MessageHandler(filters.UpdateType.EDITED_MESSAGE & filters.TEXT, deleted_edited_message)
    
    application.add_handler(edit_handler)
    
    print("Bot yayında, tepki/edit ayrımı aktif.")
    application.run_polling()
