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

# --- Tugmalar to'plami ---
def menu_button():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📄 Chek yaratish")]], 
        resize_keyboard=True
    )

def cancel_button():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Click demo chek yaratish botiga xush kelibsiz.", reply_markup=menu_button())

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Amaliyot bekor qilindi.", reply_markup=menu_button())

# 1-bosqich: Ism familiya
@dp.message(F.text == "📄 Chek yaratish")
async def start_check(m: types.Message, state: FSMContext):
    await m.answer("👤 **1-qadam:** Ism va familiyani kiriting:\n(Masalan: X. KAMOLA)", 
                   reply_markup=cancel_button(), parse_mode="Markdown")
    await state.set_state(CheckState.name)

# 2-bosqich: Summa
@dp.message(CheckState.name)
async def get_name(m: types.Message, state: FSMContext):
    await state.update_data(user_name=m.text.upper())
    await m.answer("💰 **2-qadam:** O'tkazma summasini kiriting:\n(Masalan: 400 000)", 
                   reply_markup=cancel_button(), parse_mode="Markdown")
    await state.set_state(CheckState.amount)

# 3-bosqich: Vaqt
@dp.message(CheckState.amount)
async def get_amount(m: types.Message, state: FSMContext):
    await state.update_data(user_amount=m.text)
    await m.answer("⏰ **3-qadam:** Vaqtni kiriting:\n(Masalan: 20 mar 8:34)", 
                   reply_markup=cancel_button(), parse_mode="Markdown")
    await state.set_state(CheckState.time)

# Yakuniy qism: Chek generatsiyasi
@dp.message(CheckState.time)
async def generate_final_check(m: types.Message, state: FSMContext):
    user_data = await state.get_data()
    v_name = user_data.get('user_name')
    v_amount = user_data.get('user_amount')
    v_time = m.text
    
    msg = await m.answer("⏳ Chek tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        img = Image.new('RGB', (500, 800), color=(18, 18, 18))
        d = ImageDraw.Draw(img)
        
        # Dizayn elementlari
        d.ellipse((210, 60, 290, 140), fill=(40, 180, 70)) 
        d.line((235, 100, 245, 115, 270, 90), fill=(255, 255, 255), width=5)
        d.text((150, 170), "O'tkazma amalga oshirildi", fill=(40, 180, 70))
        d.text((210, 210), v_time, fill=(150, 150, 150))
        d.text((170, 260), f"{v_amount} so'm", fill=(255, 255, 255))
        
        d.rectangle((50, 350, 450, 480), fill=(30, 30, 30), outline=(60, 60, 60))
        d.rectangle((70, 380, 130, 440), fill=(0, 110, 190))
        d.text((80, 400), "CLICK", fill=(255, 255, 255))
        d.text((150, 380), v_name, fill=(255, 255, 255))
        d.text((150, 410), "8600 12** **** 7647", fill=(150, 150, 150))
        
        d.text((100, 760), "DEMO / NAMUNA - HAQIQIY EMAS", fill=(100, 100, 100))

        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        
        photo = types.BufferedInputFile(buf.read(), filename="click.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Demo chek tayyor!", reply_markup=menu_button())
        await msg.delete()
        
    except Exception as e:
        await m.answer(f"Xatolik: {e}", reply_markup=menu_button())
    
    await state.clear()

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
