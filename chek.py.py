import asyncio
import io
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw

TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class CheckState(StatesGroup):
    waiting_name = State()
    waiting_amount = State()
    waiting_time = State()

def main_menu():
    kb = [[types.KeyboardButton(text="📄 Chek yaratish")]]
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Click demo chek yaratish uchun tugmani bosing.", reply_markup=main_menu())

@dp.message(F.text == "📄 Chek yaratish")
async def start_check(m: types.Message, state: FSMContext):
    await m.answer("Ism familiyani kiriting (Masalan: X. KAMOLA):")
    await state.set_state(CheckState.waiting_name)

@dp.message(CheckState.waiting_name)
async def get_name(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text.upper())
    await m.answer("Summani kiriting (Masalan: 400 000):")
    await state.set_state(CheckState.waiting_amount)

@dp.message(CheckState.waiting_amount)
async def get_amount(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("Vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.waiting_time)

@dp.message(CheckState.waiting_time)
async def generate_final_check(m: types.Message, state: FSMContext):
    data = await state.get_data()
    await m.answer("⏳ Chek tayyorlanmoqda...")
    
    # 1. Fondagi qora rasm
    img = Image.new('RGB', (500, 800), color=(18, 18, 18))
    d = ImageDraw.Draw(img)
    
    # 2. Yashil belgi (Muvaffaqiyatli)
    d.ellipse((200, 50, 300, 150), fill=(40, 180, 70)) # Yashil doira
    d.line((230, 100, 245, 120, 275, 80), fill=(255, 255, 255), width=5) # Galochka
    
    # 3. Asosiy matnlar
    d.text((130, 180), "O'tkazma amalga oshirildi", fill=(40, 180, 70))
    d.text((210, 220), data['time'], fill=(150, 150, 150))
    d.text((150, 270), f"{data['amount']} so'm", fill=(255, 255, 255))
    
    # 4. Foydalanuvchi ma'lumotlari bo'limi (Kvadrat)
    d.rectangle((40, 350, 460, 480), fill=(30, 30, 30), outline=(50, 50, 50))
    
    # Logotip o'rniga "CLICK" yozuvini chizish (Rasm shart emas)
    d.rectangle((60, 380, 120, 440), fill=(0, 110, 190)) # Ko'k kvadrat
    d.text((65, 400), "CLICK", fill=(255, 255, 255))
    
    d.text((140, 380), data['name'], fill=(255, 255, 255))
    d.text((140, 410), "860012****7647", fill=(150, 150, 150))
    
    # 5. Pastki yozuv
    d.text((100, 750), "DEMO / NAMUNA - HAQIQIY TRANZAKSIYA EMAS", fill=(80, 80, 80))

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    
    photo = types.BufferedInputFile(buf.read(), filename="check.png")
    await bot.send_photo(m.chat.id, photo, caption="Siz so'ragan demo chek tayyor!")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
