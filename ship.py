import os
import logging
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- FLASK SUNUCUSU (7/24 Açık Kalması İçin) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    # Render genellikle 10000 portunu kullanır, otomatik algılar.
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- BOT AYARLARI ---
OWNER_ID = 6534222591
BOT_TOKEN = "8681886836:AAErlukKkic0btbGcuVYVAVpKy1FD0mhXL4"
status = {"is_active": True}

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.lower()

    # BON / BOFF
    if user_id == OWNER_ID:
        if text == ".bon":
            status["is_active"] = True
            return await update.message.reply_text("online")
        if text == ".boff":
            status["is_active"] = False
            return await update.message.reply_text("offline")

    # ADMIN / UNADMIN
    if text.startswith(".admin") or text.startswith(".unadmin"):
        if not update.message.reply_to_message:
            return await update.message.reply_text("Lütfen birini yanıtlayın.")
        
        target_user = update.message.reply_to_message.from_user
        
        try:
            if ".admin" in text:
                await context.bot.promote_chat_member(
                    chat_id=chat_id, user_id=target_user.id,
                    can_manage_chat=True, can_delete_messages=True,
                    can_restrict_members=True, can_invite_users=True, can_pin_messages=True
                )
                
                keyboard = [
                    [InlineKeyboardButton("❌ Grup bilgilerini değiştir", callback_data='n')],
                    [InlineKeyboardButton("✅ Kullanıcıları banla", callback_data='n'), 
                     InlineKeyboardButton("✅ Mesajları sil", callback_data='n')],
                    [InlineKeyboardButton("✅ Üye ekle", callback_data='n'), 
                     InlineKeyboardButton("✅ Sabit mesajlar", callback_data='n')],
                    [InlineKeyboardButton("❌ Hikayeler yayınla", callback_data='n')],
                    [InlineKeyboardButton("Kaydet ✔️", callback_data='n')]
                ]
                await update.message.reply_text(
                    f"👮 **Admin yapılmıştır.**\n\n🕹 **İzinler**\n👤 @{target_user.username} [{target_user.id}]\n• Tag: x",
                    reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown'
                )

            elif ".unadmin" in text:
                await context.bot.promote_chat_member(chat_id=chat_id, user_id=target_user.id, can_manage_chat=False)
                await update.message.reply_text(f"❌ {target_user.first_name} yetkileri çekildi.")
        except:
            await update.message.reply_text("Hata: Botun yönetici ekleme yetkisi yok.")

async def guard_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not status["is_active"]: return
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot:
                adder = update.effective_user
                mention = f"[{adder.first_name}](tg://user?id={adder.id})"
                await update.message.reply_text(f"{mention} insecure fucks your mother.", parse_mode='Markdown')
                try:
                    await context.bot.ban_chat_member(update.effective_chat.id, member.id)
                    await context.bot.ban_chat_member(update.effective_chat.id, adder.id)
                except: pass

def main():
    keep_alive() # Web sunucusunu başlat
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))
    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, guard_logic))
    application.run_polling()

if __name__ == "__main__":
    main()
