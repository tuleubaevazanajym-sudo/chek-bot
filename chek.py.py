import asyncio
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw, ImageFont

# Bot tokeningiz
TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Bot bosqichlari
class CheckState(StatesGroup):
    name = State()
    amount = State()
    time = State()

# --- Tugmalar ---
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📄 Chek yaratish")]], 
        resize_keyboard=True
    )

def cancel_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

# --- Rasm chizish funksiyasi (Siz yuborgan kod asosida) ---
def create_click_receipt(name, amount, time_str):
    canvas_w, canvas_h = 500, 950
    bg_color = (13, 13, 13)       
    card_bg = (30, 30, 30)        
    click_green = (103, 194, 58)  
    click_blue = (0, 122, 255)    
    gray_text = (150, 150, 150)

    img = Image.new('RGB', (canvas_w, canvas_h), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Shriflar (Agar arial bo'lmasa, standart yuklanadi)
    try:
        font_amount = ImageFont.load_default(size=55)
        font_status = ImageFont.load_default(size=26)
        font_name = ImageFont.load_default(size=22)
        font_time = ImageFont.load_default(size=18)
    except:
        font_amount = font_status = font_name = font_time = ImageFont.load_default()

    # 1. Asosiy box
    draw.rounded_rectangle([30, 130, 470, 520], radius=25, fill=card_bg)

    # Yashil galochka
    draw.rounded_rectangle([200, 80, 300, 180], radius=35, fill=click_green)
    draw.line([225, 130, 245, 150, 275, 110], fill="white", width=8)

    # Matnlar
    draw.text((120, 210), "O'tkazma amalga oshirildi", fill=click_green, font=font_status)
    draw.text((200, 255), time_str, fill=gray_text, font=font_time)
    draw.text((150, 310), f"{amount} so'm", fill="white", font=font_amount)

    # Nuqtali chiziq
    draw.line([60, 395, 440, 395], fill=(60, 60, 60), width=1)

    # Karta qismi
    draw.rounded_rectangle([60, 415, 110, 465], radius=8, fill="white")
    draw.text((65, 430), "click", fill=click_blue)
    
    draw.text((135, 415), name.upper(), fill="white", font=font_name)
    draw.text((135, 445), "8600 12** **** 7647", fill=gray_text, font=font_time)

    # Tayyor tugmasi
    draw.rounded_rectangle([40, 830, 460, 890], radius=15, fill=click_blue)
    draw.text((215, 845), "Tayyor", fill="white", font=font_status)

    # Bufga saqlash
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot mantiqi ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer("Salom! Click demo chek yaratuvchi botga xush kelibsiz.", reply_markup=main_menu())

@dp.message(F.text == "📄 Chek yaratish")
async def start_steps(m: types.Message, state: FSMContext):
    await m.answer("Ism familiyani kiriting (Masalan: X. KAMOLA):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def process_name(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("Summani kiriting (Masalan: 400 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def process_amount(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("Vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.time)

@dp.message(CheckState.time)
async def process_time(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ Click cheki tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        # Chekni yaratish
        photo_buf = create_click_receipt(data['name'], data['amount'], m.text)
        
        # Yuborish
        photo = types.BufferedInputFile(photo_buf.read(), filename="click_receipt.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Demo chek tayyor!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xatolik: {e}", reply_markup=main_menu())
    
    await state.clear()

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
