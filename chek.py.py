import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import io
from PIL import Image, ImageDraw
from datetime import datetime

# Bot tokeningiz (to'g'ri shaklda)
TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def generate_receipt(name, price):
    # Oq fon yaratish
    img = Image.new('RGB', (350, 450), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    # Matnlar
    d.text((110, 20), "DEMO MARKET", fill=(0,0,0))
    d.text((20, 60), "=" * 40, fill=(0,0,0))
    d.text((20, 90), f"Sana: {now}", fill=(0,0,0))
    d.text((20, 130), f"Mahsulot: {name}", fill=(0,0,0))
    d.text((20, 160), f"Narxi: {price} so'm", fill=(0,0,0))
    d.text((20, 210), "=" * 40, fill=(0,0,0))
    d.text((20, 240), f"UMUMIY: {price} so'm", fill=(0,0,0))
    d.text((110, 350), "XARIDINGIZ UCHUN", fill=(0,0,0))
    d.text((140, 370), "RAHMAT!", fill=(0,0,0))
    
    # Rasmni xotiraga saqlash
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Demo chek yaratish uchun mahsulot va narxni yozing.\nMasalan: **Olma 10000**", parse_mode="Markdown")

@dp.message()
async def msg(m: types.Message):
    try:
        parts = m.text.split()
        if len(parts) < 2:
            return await m.answer("Iltimos, nomi va narxini yozing!")
        
        price = parts[-1]
        name = " ".join(parts[:-1])
        
        img_buf = generate_receipt(name, price)
        photo = types.BufferedInputFile(img_buf.read(), filename="chek.png")
        await bot.send_photo(m.chat.id, photo, caption="Siz so'ragan demo kvitansiya.")
        
    except Exception as e:
        print(f"Xato yuz berdi: {e}")

async def main():
    print("Bot ishga tushdi... Telegramdan tekshirib ko'ring!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
