import os
import datetime
import pytz
import eyed3
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# --- CONFIG ---
TOKEN = "8638315906:AAGGSddzlLzxd6bp1NSZ8JfqDtkpUZRUwqg"
OWNER_ID = 6534222591
LOG_ID = 6534222591
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

# Eyed3'ün hata vermemesi için log seviyesini ayarla
eyed3.log.setLevel("ERROR")

GET_MP3, GET_TITLE, GET_ARTIST, GET_PHOTO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("send the mp3 file.")
    return GET_MP3

async def handle_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    attachment = update.message.audio or update.message.document
    if not attachment:
        await update.message.reply_text("please send a valid audio file.")
        return GET_MP3

    file = await attachment.get_file()
    file_path = f"t_{update.message.from_user.id}.mp3"
    await file.download_to_drive(file_path)
    
    context.user_data['path'] = file_path
    context.user_data['old_filename'] = attachment.file_name or "unknown.mp3"
    await update.message.reply_text("enter the new song title.")
    return GET_TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("enter the new artist name.")
    return GET_ARTIST

async def handle_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist'] = update.message.text
    await update.message.reply_text("send the new cover photo or /skip.")
    return GET_PHOTO

async def process_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE, photo_path=None):
    path = context.user_data.get('path')
    title = context.user_data.get('title')
    artist = context.user_data.get('artist')
    user = update.message.from_user

    try:
        # Dosyayı yükle
        audiofile = eyed3.load(path)
        
        # Eğer dosya bozuksa veya ID3 alanı yoksa zorla oluştur
        if audiofile is None:
            # Bu durumda bile dosya adını değiştirebiliriz
            new_name = f"{artist} - {title}.mp3"
        else:
            if audiofile.tag is None:
                audiofile.initTag()
            
            audiofile.tag.title = title
            audiofile.tag.artist = artist
            
            if photo_path:
                with open(photo_path, "rb") as f:
                    audiofile.tag.images.set(3, f.read(), "image/jpeg")
            
            # Değişiklikleri en uyumlu modda (v2.3) kaydet
            audiofile.tag.save(version=eyed3.id3.ID3_V2_3, encoding='utf-8')
            new_name = f"{artist} - {title}.mp3"

        # Dosyayı kullanıcıya gönder
        with open(path, 'rb') as audio_doc:
            await update.message.reply_document(document=audio_doc, filename=new_name)

        # --- LOG SİSTEMİ ---
        # Sadece başkaları kullandığında sana bildirim gelir
        if user.id != OWNER_ID:
            now = datetime.datetime.now(TR_TIMEZONE).strftime("%H:%M:%S")
            username = f"@{user.username}" if user.username else user.first_name
            log_msg = (
                f"👤 user: {username} ({user.id})\n"
                f"📝 old: {context.user_data['old_filename']}\n"
                f"✅ new: {new_name}\n"
                f"⏰ time: {now}"
            )
            await context.bot.send_message(chat_id=LOG_ID, text=log_msg)

    except Exception as e:
        await update.message.reply_text(f"error: {str(e)}.")
    finally:
        # Geçici dosyaları sil
        if path and os.path.exists(path): os.remove(path)
        if photo_path and os.path.exists(photo_path): os.remove(photo_path)

    await update.message.reply_text("process finished.")
    return ConversationHandler.END

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"c_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(photo_path)
    return await process_and_send(update, context, photo_path)

async def skip_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await process_and_send(update, context)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.AUDIO | filters.Document.ALL, handle_mp3)],
        states={
            GET_MP3: [MessageHandler(filters.AUDIO | filters.Document.ALL, handle_mp3)],
            GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
            GET_ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_artist)],
            GET_PHOTO: [
                MessageHandler(filters.PHOTO, handle_photo),
                CommandHandler('skip', skip_photo)
            ],
        },
        fallbacks=[CommandHandler('start', start)],
    )
    
    app.add_handler(conv_handler)
    app.run_polling()
