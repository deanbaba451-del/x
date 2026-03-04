import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC
import requests
import os

TOKEN = "8701523465:AAEx_og1B72TwnH0x6qf40ZpzZfk6z9YKm"
LOG_ID = 6534222591

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
    await m.answer("mp3 gönder")
    await state.set_state(Form.mp3)

@dp.message(Form.mp3, F.audio)
async def get_mp3(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.audio.file_id)
    path = file.file_path
    data = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{path}").content

    with open("song.mp3", "wb") as f:
        f.write(data)

    await state.update_data(mp3="song.mp3")
    await m.answer("yeni şarkı ismi yaz", reply_markup=skip_kb)
    await state.set_state(Form.title)

@dp.callback_query(F.data == "skip")
async def skip(c: types.CallbackQuery, state: FSMContext):
    s = await state.get_state()

    if s == Form.title.state:
        await c.message.answer("yeni sanatçı adı yaz", reply_markup=skip_kb)
        await state.set_state(Form.artist)

    elif s == Form.artist.state:
        await c.message.answer("yeni pp gönder", reply_markup=skip_kb)
        await state.set_state(Form.photo)

    elif s == Form.photo.state:
        await finish(c.message, state)

    await c.answer()

@dp.message(Form.title)
async def title(m: types.Message, state: FSMContext):
    await state.update_data(title=m.text)
    await m.answer("yeni sanatçı adı yaz", reply_markup=skip_kb)
    await state.set_state(Form.artist)

@dp.message(Form.artist)
async def artist(m: types.Message, state: FSMContext):
    await state.update_data(artist=m.text)
    await m.answer("yeni pp gönder", reply_markup=skip_kb)
    await state.set_state(Form.photo)

@dp.message(Form.photo, F.photo)
async def photo(m: types.Message, state: FSMContext):
    file = await bot.get_file(m.photo[-1].file_id)
    path = file.file_path
    data = requests.get(f"https://api.telegram.org/file/bot{TOKEN}/{path}").content

    with open("cover.jpg", "wb") as f:
        f.write(data)

    await state.update_data(photo="cover.jpg")
    await finish(m, state)

async def finish(m, state):
    data = await state.get_data()

    audio = data.get("mp3")
    title = data.get("title")
    artist = data.get("artist")
    photo = data.get("photo")

    try:
        tags = EasyID3(audio)
    except:
        tags = EasyID3()
        tags.save(audio)

    if title:
        tags["title"] = title
    if artist:
        tags["artist"] = artist

    tags.save(audio)

    if photo:
        audiof = ID3(audio)
        with open(photo, "rb") as f:
            audiof.add(APIC(
                encoding=3,
                mime="image/jpeg",
                type=3,
                desc="cover",
                data=f.read()
            ))
        audiof.save()

    await m.answer_audio(types.FSInputFile(audio))

    user = m.from_user
    if user.username:
        text = f"yeni şarkı yaptı @{user.username}"
    else:
        text = f"yeni şarkı yaptı [{user.first_name}](tg://user?id={user.id})"

    await bot.send_message(LOG_ID, text, parse_mode="Markdown")

    await state.clear()

async def main():
    await dp.start_polling(bot)

asyncio.run(main())