import os
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC

# --- SETTINGS ---
TOKEN = "8676544410:AAEcKYZpw5dbLBgTGVZQFFac47PJ1IMt7H4" # Yeni token eklendi
OWNER_ID = 6534222591
LOG_ID = 6534222591
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

GET_MP3, GET_TITLE, GET_ARTIST, GET_PHOTO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("send the mp3 file.")
    return GET_MP3

async def handle_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.effective_attachment.get_file()
    file_path = f"t_{update.message.from_user.id}.mp3"
    await file.download_to_drive(file_path)
    context.user_data['path'] = file_path
    context.user_data['old'] = update.message.effective_attachment.file_name
    await update.message.reply_text("enter the new song title.")
    return GET_TITLE

async def handle_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['title'] = update.message.text
    await update.message.reply_text("enter the new artist name.")
    return GET_ARTIST

async def handle_artist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['artist'] = update.message.text
    await update.message.reply_text("send the new cover photo.")
    return GET_PHOTO

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = await update.message.photo[-1].get_file()
    photo_path = f"c_{update.message.from_user.id}.jpg"
    await photo_file.download_to_drive(photo_path)
    
    path = context.user_data['path']
    title = context.user_data['title']
    artist = context.user_data['artist']

    try:
        audio = MP3(path, ID3=ID3)
        try: audio.add_tags()
        except: pass
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        with open(photo_path, 'rb') as f:
            audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
        audio.save()
        
        new_name = f"{artist} - {title}.mp3"
        await update.message.reply_document(document=open(path, 'rb'), filename=new_name)
        
        # Log System
        user = update.message.from_user
        if user.id != OWNER_ID:
            now = datetime.datetime.now(TR_TIMEZONE).strftime("%H:%M:%S")
            # Mention or profile link
            mention = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
            
            log = (f"log: {mention} ({user.id})\nold: {context.user_data['old']}\nnew: {new_name}\ntime: {now}")
            await context.bot.send_message(chat_id=LOG_ID, text=log, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"an error occurred: {e}.")
    finally:
        if os.path.exists(path): os.remove(path)
        if os.path.exists(photo_path): os.remove(photo_path)

    await update.message.reply_text("process finished.")
    return ConversationHandler.END

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.Document.MP3 | filters.AUDIO, handle_mp3)],
        states={
            GET_MP3: [MessageHandler(filters.Document.MP3 | filters.AUDIO, handle_mp3)],
            GET_TITLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_title)],
            GET_ARTIST: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_artist)],
            GET_PHOTO: [MessageHandler(filters.PHOTO, handle_photo)],
        },
        fallbacks=[CommandHandler('start', start)],
    ))
    app.run_polling()
