import os
import re
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- FLASK (Render İçin) ---
app = Flask('')
@app.route('/')
def home(): return "Bot Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- AYARLAR ---
OWNER_ID = 6534222591
BOT_TOKEN = "TOKEN_BURAYA"
status = {"is_active": True}

async def promote_user(chat_id, user_id, context):
    """Kullanıcıyı gerçek admin yapar."""
    return await context.bot.promote_chat_member(
        chat_id=chat_id, user_id=user_id,
        can_manage_chat=True, can_delete_messages=True,
        can_restrict_members=True, can_invite_users=True, can_pin_messages=True
    )

async def handle_all_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()

    # 1. BON / BOFF (Sadece Sahibi)
    if user_id == OWNER_ID:
        if text == ".bon":
            status["is_active"] = True
            return await update.message.reply_text("online")
        if text == ".boff":
            status["is_active"] = False
            return await update.message.reply_text("offline")

    # 2. ,ADMIN (Reply, ID veya Mention)
    if text.startswith(",admin"):
        target_id = None
        
        # A) Yanıtlanmış Mesaj Varsa
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        
        # B) ID veya Mention Varsa (Örn: ,admin 12345 veya ,admin @kullanici)
        else:
            args = text.split()
            if len(args) > 1:
                input_val = args[1]
                if input_val.isdigit(): # ID ise
                    target_id = int(input_val)
                elif update.message.entities: # Mention ise
                    for entity in update.message.entities:
                        if entity.type == "mention":
                            # Botun kullanıcıyı tanıması için grupta olması lazım
                            # Bu basit versiyonda username'den ID çözmek zordur, reply en garantisidir.
                            pass

        if not target_id:
            return await update.message.reply_text("❌ Lütfen birini yanıtlayın veya ID yazın: `,admin 123456`")

        try:
            await promote_user(chat_id, target_id, context)
            
            # Görseldeki İzinler Menüsü
            keyboard = [
                [InlineKeyboardButton("❌ Grup bilgilerini değiştir", callback_data='n')],
                [InlineKeyboardButton("✅ Kullanıcıları banla", callback_data='n'), InlineKeyboardButton("✅ Mesajları sil", callback_data='n')],
                [InlineKeyboardButton("✅ Üye ekle", callback_data='n'), InlineKeyboardButton("✅ Sabit mesajlar", callback_data='n')],
                [InlineKeyboardButton("❌ Hikayeler yayınla", callback_data='n')],
                [InlineKeyboardButton("Kaydet ✔️", callback_data='n')]
            ]
            await update.message.reply_text(
                f"👮 **Admin yapılmıştır.**\n\n🕹 **İzinler**\n👤 ID: `{target_id}`\n• Tag: x",
                reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.MARKDOWN
            )
        except Exception as e:
            await update.message.reply_text(f"Hata: {e}")

async def guard_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not status["is_active"]: return
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot:
                adder = update.effective_user
                mention = f"[{adder.first_name}](tg://user?id={adder.id})"
                await update.message.reply_text(f"{mention} insecure fucks your mother.", parse_mode=ParseMode.MARKDOWN)
                try:
                    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=member.id)
                    await context.bot.ban_chat_member(chat_id=update.effective_chat.id, user_id=adder.id)
                except: pass

def main():
    Thread(target=run).start()
    # ÖNEMLİ: application oluştururken mesaj okuma iznini aktif ediyoruz
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all_messages))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, guard_logic))
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
