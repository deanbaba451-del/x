import os
import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC

# --- CONFIG ---
TOKEN = "8676544410:AAGg22Zv_uNvVkw8O0WPBLZROl7iQ0Fj7lk" # Yeni token eklendi
OWNER_ID = 6534222591
LOG_ID = 6534222591
TR_TIMEZONE = pytz.timezone('Europe/Istanbul')

GET_MP3, GET_TITLE, GET_ARTIST, GET_PHOTO = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("send the mp3 file.")
    return GET_MP3

async def handle_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Hem dosya hem müzik formatını algılar
    attachment = update.message.audio or update.message.document
    if not attachment or (update.message.document and not update.message.document.mime_type.startswith('audio/')):
        await update.message.reply_text("please send a valid audio file.")
        return GET_MP3

    file = await attachment.get_file()
    file_path = f"t_{update.message.from_user.id}.mp3"
    await file.download_to_drive(file_path)
    
    context.user_data['path'] = file_path
    context.user_data['old'] = attachment.file_name or "unknown.mp3"
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

async def process_and_send(update, context, photo_path=None):
    path = context.user_data['path']
    title = context.user_data['title']
    artist = context.user_data['artist']

    try:
        audio = MP3(path, ID3=ID3)
        try: audio.add_tags()
        except: pass
        
        audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TPE1(encoding=3, text=artist))
        
        if photo_path:
            with open(photo_path, 'rb') as f:
                audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
        
        audio.save()
        
        new_name = f"{artist} - {title}.mp3"
        await update.message.reply_document(document=open(path, 'rb'), filename=new_name)
        
        # Log system
        user = update.message.from_user
        if user.id != OWNER_ID:
            now = datetime.datetime.now(TR_TIMEZONE).strftime("%H:%M:%S")
            mention = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
            log = (f"log: {mention} ({user.id})\nold: {context.user_data['old']}\nnew: {new_name}\ntime: {now}")
            await context.bot.send_message(chat_id=LOG_ID, text=log, parse_mode='Markdown')

    except Exception as e:
        await update.message.reply_text(f"error: {e}.")
    finally:
        if os.path.exists(path): os.remove(path)
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
