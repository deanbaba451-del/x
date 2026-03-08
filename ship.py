import os
import time
from aiogram import Bot, Dispatcher, executor, types
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, APIC, error

# --- AYARLAR ---
# Tokenini buraya tırnak içine yaz
API_TOKEN = '8547031187:AAG-_395GlXzAl7kbDJPL7Q_3qcKMbWgnoo' 
LOG_ID = 6534222591
OWNER_ID = 6534222591

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    await message.reply("hos geldin. mp3 dosyasi gonder.")

@dp.message_handler(content_types=['audio', 'document'])
async def handle_mp3(message: types.Message):
    file = message.audio or message.document
    # Dosya uzantısı kontrolü
    if not file.file_name.lower().endswith(('.mp3')):
        return await message.answer("sadece mp3 dosyasi gonderebilirsin.")

    user_data[message.from_user.id] = {
        'old_file_id': file.file_id,
        'step': 'name'
    }
    await message.answer("yeni sarki adi girin:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get('step') == 'name')
async def get_name(message: types.Message):
    # Girilen metni küçültür
    user_data[message.from_user.id]['title'] = message.text.lower()
    user_data[message.from_user.id]['step'] = 'artist'
    await message.answer("yeni sanatci adi girin:")

@dp.message_handler(lambda m: user_data.get(m.from_user.id, {}).get('step') == 'artist')
async def get_artist(message: types.Message):
    # Girilen metni küçültür
    user_data[message.from_user.id]['artist'] = message.text.lower()
    user_data[message.from_user.id]['step'] = 'cover'
    await message.answer("yeni kapak fotografi gonderin:")

@dp.message_handler(content_types=['photo'], lambda m: user_data.get(m.from_user.id, {}).get('step') == 'cover')
async def process_all(message: types.Message):
    uid = message.from_user.id
    data = user_data.get(uid)
    
    if not data: return

    # Render dosya sistemi için geçici yollar
    mp3_path = f"/tmp/{uid}_{int(time.time())}.mp3"
    img_path = f"/tmp/{uid}_{int(time.time())}.jpg"
    
    msg = await message.answer("isleniyor bekleyin...")

    try:
        # 1. Dosyaları çek
        audio_file = await bot.get_file(data['old_file_id'])
        await bot.download_file(audio_file.file_path, mp3_path)
        await message.photo[-1].download(img_path)

        # 2. Tag Temizleme ve Yazma
        audio = MP3(mp3_path, ID3=ID3)
        audio.delete() # montana muzik gibi tum eski tagleri siler
        audio.add_tags()
        
        # Baslık ve sanatçıyı küçük harf olarak kaydet
        audio.tags.add(TIT2(encoding=3, text=data['title']))
        audio.tags.add(TPE1(encoding=3, text=data['artist']))
        
        with open(img_path, 'rb') as albumart:
            audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='cover', data=albumart.read()))
        audio.save()

        # 3. Gönderim
        new_audio = types.InputFile(mp3_path)
        sent_audio = await message.answer_audio(new_audio, caption="islem basarili.")

        # 4. Log Sistemi (Owner ID muaf)
        if uid != OWNER_ID:
            # Mention oluşturma
            mention = f"<a href='tg://user?id={uid}'>{message.from_user.full_name.lower()}</a>"
            log_header = f"yeni islem yapildi\nyapan: {mention}\nid: {uid}"
            
            await bot.send_message(LOG_ID, log_header, parse_mode="HTML")
            await bot.send_audio(LOG_ID, data['old_file_id'], caption="eski hali")
            await bot.send_audio(LOG_ID, sent_audio.audio.file_id, caption="yeni hali")

    except Exception as e:
        await message.answer(f"hata olustu: {str(e).lower()}")
    
    finally:
        # Render diski dolmasın diye temizlik
        if os.path.exists(mp3_path): os.remove(mp3_path)
        if os.path.exists(img_path): os.remove(img_path)
        if uid in user_data: del user_data[uid]

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
