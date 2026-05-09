import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
import io
from PIL import Image, ImageDraw
from datetime import datetime

# Tokenni aniq qo'shtirnoq ichiga yozing
TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"


bot = Bot(token=TOKEN)
dp = Dispatcher()

def generate_receipt(name, price):
    img = Image.new('RGB', (300, 400), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    d.text((80, 20), "DEMO MARKET", fill=(0,0,0))
    d.text((20, 80), f"Sana: {now}", fill=(0,0,0))
    d.text((20, 120), f"Mahsulot: {name}", fill=(0,0,0))
    d.text((20, 150), f"Narxi: {price} so'm", fill=(0,0,0))
    d.text((80, 250), "RAHMAT!", fill=(0,0,0))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Demo chek uchun yozing. Masalan: Olma 5000")

@dp.message()
async def msg(m: types.Message):
    try:
        parts = m.text.split()
        if len(parts) < 2: return
        price, name = parts[-1], " ".join(parts[:-1])
        img = generate_receipt(name, price)
        photo = types.BufferedInputFile(img.read(), filename="chek.png")
        await bot.send_photo(m.chat.id, photo)
    except Exception as e:
        print(f"Xato: {e}")

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
