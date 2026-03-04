import asyncio
import os
import requests
from datetime import datetime
import pytz 

from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from mutagen.id3 import ID3, APIC, TIT2, TPE1

# --- AYARLAR ---
TOKEN = "8701523465:AAEx_og1B72TwnH0x6qf40ZpzZfk6z9YKmA"
LOG_ID = 6534222591
OWNER_ID = 6534222591 # Senin ID'n

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    mp3 = State()
    title = State()
    artist = State()
    photo = State()

skip_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="atla", callback_data="skip")]]
)

@dp.message(CommandStart())
async def start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("🎵 Hoş geldin! Lütfen düzenlemek istediğin **mp3 dosyasını** gönder.")
    await state.set_state(Form.mp3)

# Hem Audio hem Document (MP3) kabul etmesi için güncellendi
@dp.message(Form.mp3, (F.audio | F.document))
async def get_mp3(m: types.Message, state: FSMContext):
    # Dosya ID'sini al
    file_id = m.audio.file_id if m.audio else m.document.file_id
    
    # MP3 kontrolü
    if m.document and not m.document.file_name.endswith('.mp3'):
        return await m.answer("Lütfen sadece .mp3 formatında dosya gönder.")

    old_title = m.audio.title if (m.audio and m.audio.title) else "Bilinmiyor"
    old_artist = m.audio.performer if (m.audio and m.audio.performer) else "Bilinmiyor"
    
    msg = await m.answer("⏳ Dosya indiriliyor, lütfen bekleyin...")
    
    file = await bot.get_file(file_id)
    content = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}").content

    file_name = f"temp_{m.from_user.id}.mp3"
    with open(file_name, "wb") as f:
        f.write(content)

    await state.update_data(mp3=file_name, old_t=old_title, old_a=old_artist)
    await msg.edit_text(f"✅ İndirildi.\n\n**Eski İsim:** {old_title}\n**Yeni şarkı ismi ne olsun?**", reply_markup=skip_kb, parse_mode="Markdown")
    await state.set_state(Form.title)

@dp.callback_query(F.data == "skip")
async def skip(c: types.CallbackQuery, state: FSMContext):
    curr = await state.get_state()
    if curr == Form.title.state:
        await c.message.answer("Yeni sanatçı adı ne olsun?", reply_markup=skip_kb)
        await state.set_state(Form.artist)
    elif curr == Form.artist.state:
        await c.message.answer("Yeni kapak fotoğrafını (Kare olması önerilir) gönder:", reply_markup=skip_kb)
        await state.set_state(Form.photo)
    elif curr == Form.photo.state:
        await finish_process(c.message, state)
    await c.answer()

@dp.message(Form.title)
async def set_title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text)
    await m.answer("Yeni sanatçı adı ne olsun?", reply_markup=skip_kb)
    await state.set_state(Form.artist)

@dp.message(Form.artist)
async def set_artist(m: types.Message, state: FSMContext):
    await state.update_data(artist=m.text)
    await m.answer("Yeni kapak fotoğrafını gönder:", reply_markup=skip_kb)
    await state.set_state(Form.photo)

@dp.message(Form.photo, F.photo)
async def set_photo(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    content = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}").content
    img_name = f"img_{m.from_user.id}.jpg"
    with open(img_name, "wb") as f:
        f.write(content)
    await state.update_data(photo=img_name)
    await finish_process(m, state)

async def finish_process(m, state):
    data = await state.get_data()
    audio_path = data.get("mp3")
    new_t = data.get("title")
    new_a = data.get("artist")
    photo_path = data.get("photo")

    await m.answer("⚙️ Dosya işleniyor ve kapak fotoğrafı gömülüyor...")

    try:
        # Etiketleme ve Resim Gömme
        audio = ID3(audio_path)
        if new_t: audio.add(TIT2(encoding=3, text=new_t))
        if new_a: audio.add(TPE1(encoding=3, text=new_a))
        if photo_path:
            with open(photo_path, "rb") as f:
                audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc=u'Cover', data=f.read()))
        audio.save(v2_version=3)

        # Gönderim
        await m.answer_audio(types.FSInputFile(audio_path), caption="✨ İşlem başarıyla tamamlandı!")

        # Log (Owner değilse)
        if m.from_user.id != OWNER_ID:
            tr_tz = pytz.timezone('Europe/Istanbul')
            saat_tarih = datetime.now(tr_tz).strftime('%d.%m.%Y | %H:%M:%S')
            user = m.from_user
            u_link = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
            
            log_text = (
                f"🎵 **Şarkı Düzenlendi**\n"
                f"👤 **Kullanıcı:** {u_link}\n"
                f"📥 **Eski:** {data.get('old_a')} - {data.get('old_t')}\n"
                f"📤 **Yeni:** {new_a or 'Aynı'} - {new_t or 'Aynı'}\n"
                f"⏰ **Zaman:** `{saat_tarih}`"
            )
            await bot.send_message(LOG_ID, log_text, parse_mode="Markdown")

    except Exception as e:
        await m.answer(f"❌ Bir hata oluştu: {e}")

    # Temizlik
    if os.path.exists(audio_path): os.remove(audio_path)
    if photo_path and os.path.exists(photo_path): os.remove(photo_path)
    await state.clear()

async def main():
    print("Bot çalışıyor...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
