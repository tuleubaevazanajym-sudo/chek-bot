import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from PIL import Image, ImageDraw
import io
from datetime import datetime

# Bot tokeningiz
TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def generate_receipt(item_name, price):
    img = Image.new('RGB', (300, 420), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    now = datetime.now().strftime("%d.%m.%Y %H:%M")
    
    d.text((80, 20), "DEMO CHECKOUT", fill=(0,0,0))
    d.text((20, 50), "=" * 35, fill=(0,0,0))
    d.text((20, 80), f"Sana: {now}", fill=(0,0,0))
    d.text((20, 110), f"Chek raqami: #12345", fill=(0,0,0))
    d.text((20, 150), "-" * 35, fill=(0,0,0))
    d.text((20, 180), f"Mahsulot: {item_name}", fill=(0,0,0))
    d.text((20, 210), f"Narxi: {price} so'm", fill=(0,0,0))
    d.text((20, 250), "-" * 35, fill=(0,0,0))
    d.text((20, 280), f"UMUMIY: {price} so'm", fill=(0,0,0))
    d.text((20, 320), "=" * 35, fill=(0,0,0))
    d.text((60, 350), "BU FAQAT DEMO VARIANT", fill=(150,150,150))
    d.text((90, 370), "Xarid uchun rahmat!", fill=(0,0,0))
    
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.reply("Salom! Demo chek uchun: **Mahsulot Narx** formatida yozing.")

@dp.message()
async def handle_text(message: types.Message):
    try:
        parts = message.text.split()
        if len(parts) < 2: return
        price, name = parts[-1], " ".join(parts[:-1])
        receipt_img = generate_receipt(name, price)
        photo = types.BufferedInputFile(receipt_img.read(), filename="demo.png")
        await bot.send_photo(chat_id=message.chat.id, photo=photo)
    except: pass

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
Python 3.14.4 (tags/v3.14.4:23116f9, Apr  7 2026, 14:10:54) [MSC v.1944 64 bit (AMD64)] on win32
Enter "help" below or click "Help" above for more information.
