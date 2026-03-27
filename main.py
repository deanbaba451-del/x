import json
import asyncio
import instaloader
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# --- ayarlar ---
api_token = '8234467575:AAF2aOti1T-uKDItPMoREmZU0j5GAJB_VOQ'
owner_id = 6534222591
friend_id = 8656150458 # yeni eklenen arkadas id
data_file = 'data.json'

bot = Bot(token=api_token)
dp = Dispatcher(bot)
L = instaloader.Instaloader()

# --- render uyku modu engelleyici (http server) ---
async def handle(request):
    return web.Response(text="stalker bot aktif ve nobette")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000)
    await site.start()

# --- veritabanı ---
def get_db():
    try:
        with open(data_file, 'r') as f: return json.load(f)
    except: return {"ig": {}, "yetkili": [owner_id, friend_id]}

def save_db(data):
    with open(data_file, 'w') as f: json.dump(data, f)

# --- butonlar ---
def ana_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("➕ hedef ekle", callback_data="ekle"),
        types.InlineKeyboardButton("📋 liste", callback_data="liste"),
        types.InlineKeyboardButton("🧹 listeyi temizle", callback_data="temizle")
    )
    return kb

@dp.message_handler(commands=['start'])
async def start(m: types.Message):
    db = get_db()
    if m.from_user.id in db["yetkili"]:
        await m.answer("islem sec kanka", reply_markup=ana_menu())

@dp.callback_query_handler(lambda c: c.data == "ekle")
async def ekle_btn(c: types.CallbackQuery):
    await c.message.answer("izlenecek instagram kullanici adini yaz (basinda @ olmadan):")

@dp.callback_query_handler(lambda c: c.data == "liste")
async def liste_btn(c: types.CallbackQuery):
    db = get_db()
    txt = "📋 izleme listesi:\n\n"
    if not db["ig"]:
        txt += "liste bos"
    else:
        for u, d in db["ig"].items():
            txt += f"• @{u} (takipci: {d['tkp']} / post: {d['post']})\n"
    await c.message.edit_text(txt.lower(), reply_markup=ana_menu())

@dp.callback_query_handler(lambda c: c.data == "temizle")
async def temizle_btn(c: types.CallbackQuery):
    db = get_db()
    db["ig"] = {}
    save_db(db)
    await c.message.edit_text("liste temizlendi", reply_markup=ana_menu())

@dp.message_handler()
async def isim_al(m: types.Message):
    db = get_db()
    if m.from_user.id in db["yetkili"]:
        user = m.text.lower().replace("@", "").strip()
        db["ig"][user] = {"tkp": 0, "edilen": 0, "post": 0}
        save_db(db)
        await m.answer(f"@{user} takibe alindi. ilk veriler 5 dk icinde gelir.", reply_markup=ana_menu())

# --- stalk motoru ---
async def stalk_loop():
    while True:
        db = get_db()
        for target, eski in db["ig"].items():
            try:
                p = instaloader.Profile.from_username(L.context, target)
                y = {"tkp": p.followers, "edilen": p.followees, "post": p.mediacount}
                
                if eski["tkp"] != 0:
                    rapor = ""
                    if y["tkp"] != eski["tkp"]:
                        fark = y["tkp"] - eski["tkp"]
                        durum = "artti" if fark > 0 else "dustu"
                        rapor += f"👤 takipci {durum}: {abs(fark)} (toplam: {y['tkp']})\n"
                    if y["edilen"] != eski["edilen"]:
                        fark = y["edilen"] - eski["edilen"]
                        durum = "takibe aldi" if fark > 0 else "takipten cikti"
                        rapor += f"🔍 {durum} (toplam: {y['edilen']})\n"
                    if y["post"] > eski["post"]:
                        post = next(p.get_posts())
                        rapor += f"📸 yeni paylasim: https://instagram.com/p/{post.shortcode}\n"
                    
                    if rapor:
                        for kisi in db["yetkili"]:
                            try: await bot.send_message(kisi, f"🔔 @{target} hareketlilik:\n\n{rapor.lower()}")
                            except: pass
                
                db["ig"][target] = y
            except: continue
        
        save_db(db)
        await asyncio.sleep(300)

# --- bot baslaticilari ---
async def on_startup(_):
    asyncio.create_task(start_server())
    asyncio.create_task(stalk_loop())

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False, on_startup=on_startup)
