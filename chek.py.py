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
    # Foydalanuvchiga jarayon boshlanganini bildirish
    msg = await m.answer("⏳ Chek generatsiya qilinmoqda...")
    
    try:
        # 1. Fondagi qora rasm (hajmi 500x800)
        img = Image.new('RGB', (500, 800), color=(18, 18, 18))
        d = ImageDraw.Draw(img)
        
        # 2. Yashil belgi (Muvaffaqiyatli doira)
        d.ellipse((210, 60, 290, 140), fill=(40, 180, 70)) 
        # Galochka chizish
        d.line((235, 100, 245, 115, 270, 90), fill=(255, 255, 255), width=4)
        
        # 3. Asosiy matnlar (Soddaroq koordinatalar)
        d.text((150, 170), "O'tkazma amalga oshirildi", fill=(40, 180, 70))
        d.text((210, 210), data['time'], fill=(150, 150, 150))
        d.text((180, 260), f"{data['amount']} so'm", fill=(255, 255, 255))
        
        # 4. Markaziy ma'lumotlar bloki (To'rtburchak)
        d.rectangle((50, 350, 450, 480), outline=(60, 60, 60), width=2)
        
        # Logotip o'rni (ko'k kvadrat)
        d.rectangle((70, 380, 130, 440), fill=(0, 110, 190)) 
        d.text((80, 400), "CLICK", fill=(255, 255, 255))
        
        # Ism va karta raqami
        d.text((150, 385), data['name'], fill=(255, 255, 255))
        d.text((150, 415), "8600 12** **** 7647", fill=(150, 150, 150))
        
        # 5. Eslatma matni
        d.text((80, 750), "DEMO / NAMUNA - HAQIQIY TRANZAKSIYA EMAS", fill=(100, 100, 100))

        # Rasmni jo'natish uchun tayyorlash
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        # Bot orqali yuborish
        photo = types.BufferedInputFile(buf.read(), filename="click_demo.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Demo chek muvaffaqiyatli tayyorlandi.")
        await msg.delete() # Kutish haqidagi xabarni o'chirish
        
    except Exception as e:
        await m.answer(f"Xatolik yuz berdi: {e}")
    
    await state.clear()

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
