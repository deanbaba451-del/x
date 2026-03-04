import asyncio, os, requests, pytz
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from mutagen.id3 import ID3, APIC, TIT2, TPE1

# --- AYARLAR ---
TOKEN = "8701523465:AAFElcMm72FKQS4C-WQf-NHJh9IdTwnKb0w"
LOG_ID = 6534222591
OWNER_ID = 6534222591 

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

class Form(StatesGroup):
    mp3 = State()
    title = State()
    artist = State()
    photo = State()

atla_kb = types.InlineKeyboardMarkup(inline_keyboard=[[types.InlineKeyboardButton(text="atla.", callback_data="skip")]])

@dp.message(CommandStart())
async def start(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("mp3 gönder.")
    await state.set_state(Form.mp3)

@dp.message(Form.mp3, (F.audio | F.document))
async def get_mp3(m: types.Message, state: FSMContext):
    fid = m.audio.file_id if m.audio else m.document.file_id
    if m.document and not m.document.file_name.lower().endswith('.mp3'):
        return
    
    # Mevcut bilgileri al
    et = m.audio.title if (m.audio and m.audio.title) else "Bilinmeyen Şarkı."
    es = m.audio.performer if (m.audio and m.audio.performer) else "Bilinmeyen Sanatçı."
    
    file = await bot.get_file(fid)
    res = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{file.file_path}").content
    # Çakışma olmaması için kullanıcı ID'li isim kullanıyoruz
    path = f"file_{m.from_user.id}.mp3"
    with open(path, "wb") as f: f.write(res)

    await state.update_data(mp3=path, et=et, es=es)
    await m.answer("yeni isim?", reply_markup=atla_kb)
    await state.set_state(Form.title)

@dp.callback_query(F.data == "skip")
async def skip(c: types.CallbackQuery, state: FSMContext):
    s = await state.get_state()
    if s == Form.title.state:
        await c.message.delete()
        await c.message.answer("yeni sanatçı?", reply_markup=atla_kb)
        await state.set_state(Form.artist)
    elif s == Form.artist.state:
        await c.message.delete()
        await c.message.answer("yeni profil?", reply_markup=atla_kb)
        await state.set_state(Form.photo)
    elif s == Form.photo.state:
        await c.message.delete()
        await finish(c.message, state)
    await c.answer()

@dp.message(Form.title)
async def st(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text)
    await m.answer("yeni sanatçı?", reply_markup=atla_kb)
    await state.set_state(Form.artist)

@dp.message(Form.artist)
async def sa(m: types.Message, state: FSMContext):
    await state.update_data(artist=m.text)
    await m.answer("yeni profil?", reply_markup=atla_kb)
    await state.set_state(Form.photo)

@dp.message(Form.photo, F.photo)
async def sp(m: types.Message, state: FSMContext):
    f = await bot.get_file(m.photo[-1].file_id)
    res = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{f.file_path}").content
    p = f"img_{m.from_user.id}.jpg"
    with open(p, "wb") as f: f.write(res)
    await state.update_data(photo=p)
    await finish(m, state)

async def finish(m, state):
    d = await state.get_data()
    path, nt, na, ph = d.get("mp3"), d.get("title"), d.get("artist"), d.get("photo")

    try:
        # ID3 Etiketleme
        audio = ID3(path)
        audio.add(TIT2(encoding=3, text=nt if nt else d.get("et")))
        audio.add(TPE1(encoding=3, text=na if na else d.get("es")))
        
        if ph:
            with open(ph, "rb") as f:
                audio.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=f.read()))
        audio.save(v2_version=3)

        # Şarkıyı gönder
        await m.answer_audio(types.FSInputFile(path))

        # Log sistemi (Owner değilse çalışır)
        if m.from_user.id != OWNER_ID:
            tz = pytz.timezone('Europe/Istanbul')
            z = datetime.now(tz).strftime('%H:%M')
            u = f"@{m.from_user.username}" if m.from_user.username else m.from_user.first_name
            log = f"👤 {u}.\n📝 {na or d.get('es')} - {nt or d.get('et')}.\n⏰ {z}."
            await bot.send_message(LOG_ID, log)

    except Exception as e:
        # Hata durumunda kullanıcıya bilgi ver
        await m.answer("işlem sırasında hata oluştu.")
        print(f"Hata detayı: {e}")

    # Dosya temizliği (Sadece dosya varsa sil)
    if path and os.path.exists(path): os.remove(path)
    if ph and os.path.exists(ph): os.remove(ph)
    await state.clear()

async def main(): 
    print("Bot aktif.")
    await dp.start_polling(bot)

if __name__ == "__main__": 
    asyncio.run(main())
