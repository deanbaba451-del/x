import json
import asyncio
import instaloader
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiohttp import web

# --- ayarlar ---
api_token = '8234467575:AAF2aOti1T-uKDItPMoREmZU0j5GAJB_VOQ'
owner_id = 6534222591
data_file = 'data.json'

bot = Bot(token=api_token)
dp = Dispatcher(bot)
L = instaloader.Instaloader()

# --- render uyku modu engelleyici (http server) ---
async def handle(request):
    return web.Response(text="bot aktif")

async def start_server():
    app = web.Application()
    app.router.add_get('/', handle)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 10000) # render genelde 10000 portunu ister
    await site.start()

# --- veritabanı ---
def get_db():
    try:
        with open(data_file, 'r') as f: return json.load(f)
    except: return {"ig": {}, "yetkili": [owner_id]}

def save_db(data):
    with open(data_file, 'w') as f: json.dump(data, f)

# --- stalk motoru ---
async def stalk_loop():
    while True:
        db = get_db()
        rapor = ""
        for target, eski in db["ig"].items():
            try:
                p = instaloader.Profile.from_username(L.context, target)
                y = {"tkp": p.followers, "edilen": p.followees, "post": p.mediacount}
                
                if eski["tkp"] != 0:
                    degisim = ""
                    if y["tkp"] != eski["tkp"]:
                        degisim += f"👤 takipçi: {y['tkp']} ({y['tkp']-eski['tkp']})\n"
                    if y["edilen"] != eski["edilen"]:
                        degisim += f"🔍 takip edilen: {y['edilen']} ({y['edilen']-eski['edilen']})\n"
                    if y["post"] > eski["post"]:
                        post = next(p.get_posts())
                        degisim += f"📸 yeni post: https://instagram.com/p/{post.shortcode}\n"
                    
                    if degisim:
                        rapor += f"🔔 @{target}\n{degisim}\n"

                db["ig"][target] = y
            except: continue
        
        if rapor:
            for kisi in db["yetkili"]:
                try: await bot.send_message(kisi, rapor.lower())
                except: pass
            save_db(db)
        
        await asyncio.sleep(300) # 5 dk bekle

# --- başlatma ---
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(start_server()) # web sunucusunu başlat
    loop.create_task(stalk_loop())   # stalk motorunu başlat
    executor.start_polling(dp, skip_updates=True)
