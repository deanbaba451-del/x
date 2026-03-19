import os
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- FLASK ---
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

# --- YETKİ PANELİ TASARIMI ---
def get_admin_keyboard(user_id):
    # Görseldeki tüm butonlar ve callback dataları
    keyboard = [
        [InlineKeyboardButton("❌ Grup bilgilerini değiştir", callback_data=f"perm_info_{user_id}")],
        [InlineKeyboardButton("✅ Kullanıcıları banla", callback_data=f"perm_ban_{user_id}"), 
         InlineKeyboardButton("✅ Mesajları sil", callback_data=f"perm_del_{user_id}")],
        [InlineKeyboardButton("✅ Üye ekle", callback_data=f"perm_invite_{user_id}"), 
         InlineKeyboardButton("✅ Sabit mesajlar", callback_data=f"perm_pin_{user_id}")],
        [InlineKeyboardButton("❌ Hikayeler yayınla", callback_data=f"perm_story_{user_id}")],
        [InlineKeyboardButton("Kaydet ✔️", callback_data="save_perms")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- BUTONLARA BASINCA ÇALIŞACAK KISIM ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data
    await query.answer() # Butonun dönmesini (loading) durdurur

    if data == "save_perms":
        await query.edit_message_text("✅ Değişiklikler başarıyla kaydedildi.")
        return

    if data.startswith("perm_"):
        # Burada basılan butona göre grupta yetki güncellenir
        # Örnek: perm_ban_12345 -> [2] id'li kişiyi ban yetkisiyle günceller
        parts = data.split("_")
        target_id = int(parts[2])
        # Gerçek yetki verme (Örnek: Ban yetkisi)
        try:
            # Burası basılan butona göre dinamikleştirilebilir, şu an sadece loadingi durdurur.
            await query.answer(text="Yetki güncellendi (Simülasyon)", show_alert=False)
        except: pass

async def handle_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip().lower()

    # .bon / .boff
    if user_id == OWNER_ID:
        if text == ".bon":
            status["is_active"] = True
            return await update.message.reply_text("online")
        if text == ".boff":
            status["is_active"] = False
            return await update.message.reply_text("offline")

    # ,admin (Reply veya ID)
    if text.startswith(",admin"):
        target_id = None
        if update.message.reply_to_message:
            target_id = update.message.reply_to_message.from_user.id
        else:
            args = text.split()
            if len(args) > 1 and args[1].isdigit(): target_id = int(args[1])

        if not target_id: return

        try:
            # 1. Önce grupta admin yap
            await context.bot.promote_chat_member(
                chat_id=chat_id, user_id=target_id,
                can_manage_chat=True, can_delete_messages=True,
                can_restrict_members=True, can_invite_users=True, can_pin_messages=True
            )
            
            # 2. Grupta bilgi mesajı at
            await update.message.reply_text(f"👮 **Admin yapılmıştır.**\n• Tag: x\n\n📩 Panel DM kutunuza gönderildi.")

            # 3. DM'den PANELİ AT (Görseldeki gibi)
            try:
                await context.bot.send_message(
                    chat_id=user_id, # Komutu yazan kişiye DM atar
                    text=f"🕹 **İzinler**\n👤 ID: `{target_id}`\n👥 Grup: {update.effective_chat.title}\n\nAşağıdaki butonlardan yetkileri yönetebilirsiniz:",
                    reply_markup=get_admin_keyboard(target_id),
                    parse_mode=ParseMode.MARKDOWN
                )
            except:
                await update.message.reply_text("❌ Sana DM atamadım! Lütfen botu başlat (start).")

        except Exception as e:
            await update.message.reply_text(f"Hata: {e}")

async def guard_logic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not status["is_active"]: return
    if update.message.new_chat_members:
        for member in update.message.new_chat_members:
            if member.is_bot:
                adder = update.effective_user
                try:
                    await update.message.reply_text(f"[{adder.first_name}](tg://user?id={adder.id}) insecure fucks your mother.", parse_mode=ParseMode.MARKDOWN)
                    await context.bot.ban_chat_member(update.effective_chat.id, member.id)
                    await context.bot.ban_chat_member(update.effective_chat.id, adder.id)
                except: pass

def main():
    Thread(target=run).start()
    app_bot = Application.builder().token(BOT_TOKEN).build()
    
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_commands))
    app_bot.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, guard_logic))
    app_bot.add_handler(CallbackQueryHandler(button_handler)) # Butonları çalıştıran kısım
    
    app_bot.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
