import asyncio
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw

TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class CheckState(StatesGroup):
    name = State()
    amount = State()
    time = State()

def main_menu():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="📄 Chek yaratish")]], resize_keyboard=True)

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Click demo chek botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📄 Chek yaratish")
async def start_check(m: types.Message, state: FSMContext):
    await m.answer("Ism familiyani kiriting (Masalan: X. KAMOLA):")
    await state.set_state(CheckState.name)

@dp.message(CheckState.name)
async def get_name(m: types.Message, state: FSMContext):
    await state.update_data(user_name=m.text.upper())
    await m.answer("Summani kiriting (Masalan: 400 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def get_amount(m: types.Message, state: FSMContext):
    await state.update_data(user_amount=m.text)
    await m.answer("Vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.time)

@dp.message(CheckState.time)
async def generate_final_check(m: types.Message, state: FSMContext):
    data = await state.get_data()
    v_time = m.text
    msg = await m.answer("⏳ Chek tayyorlanmoqda...")
    
    try:
        # 1. Click'ga xos to'q kulrang fon
        img = Image.new('RGB', (550, 950), color=(26, 26, 26))
        d = ImageDraw.Draw(img)
        
        # 2. Yashil doira va oq galochka
        d.ellipse((225, 80, 325, 180), fill=(46, 204, 113))
        d.line((255, 130, 270, 145, 300, 110), fill=(255, 255, 255), width=6)
        
        # 3. Markaziy matnlar
        d.text((155, 220), "O'tkazma amalga oshirildi", fill=(46, 204, 113))
        d.text((245, 265), v_time, fill=(160, 160, 160)) # Sana va vaqt
        
        # Summa (Katta va oq rangda)
        d.text((150, 310), f"{data['user_amount']}", fill=(255, 255, 255))
        d.text((370, 315), "so'm", fill=(180, 180, 180))
        
        # Ajratuvchi nuqtali chiziq
        d.text((50, 380), "." * 60, fill=(80, 80, 80))
        
        # 4. Karta ma'lumotlari bloki
        # To'rtburchak fon (sal ochroq)
        d.rectangle((50, 420, 500, 560), fill=(35, 35, 35))
        
        # Click Logotipi (Ko'k kvadrat)
        d.rectangle((75, 455, 145, 525), fill=(0, 120, 215))
        d.text((85, 480), "click", fill=(255, 255, 255))
        
        # Ism va karta raqami
        d.text((170, 455), data['user_name'], fill=(255, 255, 255))
        d.text((170, 495), "8600 12** **** 7647", fill=(150, 150, 150))
        
        # 5. Pastki "Tayyor" tugmasi simulyatsiyasi
        d.rectangle((50, 830, 500, 900), fill=(0, 120, 215))
        d.text((245, 850), "Tayyor", fill=(255, 255, 255))
        
        # Eslatma
        d.text((140, 920), "DEMO - HAQIQIY TRANZAKSIYA EMAS", fill=(70, 70, 70))

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        photo = types.BufferedInputFile(buf.read(), filename="click.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Click demo chek tayyor!")
        await msg.delete()
        
    except Exception as e:
        await m.answer(f"Xato: {e}")
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
