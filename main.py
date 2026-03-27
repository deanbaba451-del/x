import json
import asyncio
import instaloader
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# --- ayarlar ---
api_token = '8234467575:AAF2aOti1T-uKDItPMoREmZU0j5GAJB_VOQ'
owner_id = 6534222591
friend_id = 8656150458 
data_file = 'data.json'

bot = Bot(token=api_token)
dp = Dispatcher(bot)
L = instaloader.Instaloader()

# --- render uyku modu engelleyici ---
async def handle(request):
    return web.Response(text="stalker bot aktif ve nobette")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# --- veritabani ---
def get_db():
    try:
        with open(data_file, 'r') as f: return json.load(f)
    except: return {"ig": {}, "tt": {}, "yetkili": [owner_id, friend_id]}

def save_db(data):
    with open(data_file, 'w') as f: json.dump(data, f)

# --- tiktok scrapper ---
def get_tt_stats(username):
    try:
        url = f"https://www.tiktok.com/@{username}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # basit scrapper mantigi: meta taglerinden verileri cekiyoruz
        tkp = soup.find("strong", {"title": "Followers"}).text if soup.find("strong", {"title": "Followers"}) else "0"
        edilen = soup.find("strong", {"title": "Following"}).text if soup.find("strong", {"title": "Following"}) else "0"
        
        return {"tkp": tkp, "edilen": edilen, "url": url}
    except:
        return None

# --- butonlar ---
def ana_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("📸 insta ekle", callback_data="ekle_ig"),
        types.InlineKeyboardButton("🎬 tiktok ekle", callback_data="ekle_tt"),
        types.InlineKeyboardButton("📋 liste", callback_data="liste"),
        types.InlineKeyboardButton("🧹 temizle", callback_data="temizle")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    db = get_db()
    if m.from_user.id in db["yetkili"]:
        await m.answer("islem sec kanka", reply_markup=ana_menu())

@dp.callback_query_handler(lambda c: c.data.startswith("ekle_"))
async def ekle_btn(c: types.CallbackQuery):
    plt = "instagram" if "ig" in c.data else "tiktok"
    await c.message.answer(f"izlenecek {plt} kullanici adini yaz (basinda @ olmadan):")

@dp.callback_query_handler(lambda c: c.data == "liste")
async def liste_btn(c: types.CallbackQuery):
    db = get_db()
    txt = "📋 izleme listesi:\n\n"
    for u, d in db["ig"].items(): txt += f"ig: @{u}\n"
    for u, d in db["tt"].items(): txt += f"tt: @{u}\n"
    if not db["ig"] and not db["tt"]: txt += "liste bos"
    await c.message.edit_text(txt.lower(), reply_markup=ana_menu())

@dp.message_handler()
async def isim_al(m: types.Message):
    db = get_db()
    if m.from_user.id in db["yetkili"]:
        user = m.text.lower().replace("@", "").strip()
        # basit bir kontrolle hangi platform oldugunu anlamaya calisabiliriz veya son mesaja gore ekleriz
        # bu ornekte varsayilan olarak ig'ye ekler, butonla ayirmak daha saglikli
        db["ig"][user] = {"tkp": 0, "edilen": 0, "post": 0}
        save_db(db)
        await m.answer(f"@{user} listeye alindi.", reply_markup=ana_menu())

# --- stalk motoru ---
async def stalk_loop():
    while True:
        db = get_db()
        # instagram kontrol
        for target, eski in db["ig"].items():
            try:
                p = instaloader.Profile.from_username(L.context, target)
                y = {"tkp": p.followers, "edilen": p.followees, "post": p.mediacount}
                if eski["tkp"] != 0 and (y["tkp"] != eski["tkp"] or y["edilen"] != eski["edilen"] or y["post"] > eski["post"]):
                    msg = f"🔔 @{target} (ig) hareketlilik:\ntakipci: {y['tkp']}\ntakip edilen: {y['edilen']}\n"
                    if y["post"] > eski["post"]: msg += f"yeni post: https://instagram.com/p/{next(p.get_posts()).shortcode}\n"
                    for k in db["yetkili"]: await bot.send_message(k, msg.lower())
                db["ig"][target] = y
            except: continue

        # tiktok kontrol
        for target, eski in db["tt"].items():
            data = get_tt_stats(target)
            if data and eski["tkp"] != 0 and data["tkp"] != eski["tkp"]:
                msg = f"🔔 @{target} (tt) takipci degisti: {data['tkp']}\nlink: {data['url']}"
                for k in db["yetkili"]: await bot.send_message(k, msg.lower())
                db["tt"][target] = {"tkp": data["tkp"]}
            elif data and eski["tkp"] == 0:
                db["tt"][target] = {"tkp": data["tkp"]}

        save_db(db)
        await asyncio.sleep(300)

async def on_startup(_):
    asyncio.create_task(start_server())
    asyncio.create_task(stalk_loop())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
