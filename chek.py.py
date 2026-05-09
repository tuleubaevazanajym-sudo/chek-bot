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

# Bot bosqichlari (FSM)
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

# --- Rasm chizish funksiyasi (Siz yuborgan V3 kod asosida) ---
def create_click_receipt_v3(name, amount, time_str):
    width, height = 500, 900
    bg_color = (15, 15, 15)       
    card_bg = (33, 33, 33)        
    click_green = (100, 190, 60)  
    click_blue = (0, 122, 255)    
    
    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Shriftlarni yuklash (Standard shriftlar ishlatiladi)
    try:
        font_main = ImageFont.load_default(size=52)
        font_status = ImageFont.load_default(size=24)
        font_text = ImageFont.load_default(size=20)
        font_small = ImageFont.load_default(size=16)
    except:
        font_main = font_status = font_text = font_small = ImageFont.load_default()

    # 1. Asosiy blok
    draw.rounded_rectangle([40, 120, 460, 500], radius=25, fill=card_bg)

    # Yashil galochka belgisi
    draw.rounded_rectangle([205, 80, 295, 170], radius=25, fill=click_green)
    draw.line([225, 125, 245, 145, 275, 105], fill="white", width=6)

    # Status matni
    status = "O'tkazma amalga oshirildi"
    w_status = draw.textlength(status, font=font_status)
    draw.text(((width - w_status) / 2, 190), status, fill=click_green, font=font_status)

    # Vaqt
    w_time = draw.textlength(time_str, font=font_small)
    draw.text(((width - w_time) / 2, 230), time_str, fill=(160, 160, 160), font=font_small)

    # Summa
    full_amount = f"{amount} so'm"
    w_amount = draw.textlength(full_amount, font=font_main)
    draw.text(((width - w_amount) / 2, 280), full_amount, fill="white", font=font_main)

    # Ajratuvchi chiziq
    draw.line([70, 370, 430, 370], fill=(60, 60, 60), width=1)

    # Karta ma'lumotlari
    draw.rounded_rectangle([70, 400, 130, 460], radius=10, fill="white")
    draw.text((78, 420), "click", fill=click_blue)

    # Ism va karta raqami
    draw.text((150, 405), name.upper(), fill="white", font=font_text)
    draw.text((150, 435), "8600 12** **** 7647", fill=(160, 160, 160), font=font_text)

    # 2. "Tayyor" tugmasi
    draw.rounded_rectangle([40, 800, 460, 860], radius=15, fill=click_blue)
    btn_text = "Tayyor"
    w_btn = draw.textlength(btn_text, font=font_status)
    draw.text(((width - w_btn) / 2, 818), btn_text, fill="white", font=font_status)

    # Faylni buferga saqlash
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Telegram Bot Mantiqi ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    await m.answer("Click V3 demo chek botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📄 Chek yaratish")
async def start_steps(m: types.Message, state: FSMContext):
    await m.answer("Ism familiyani kiriting (Masalan: X, BEGZOD):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Jarayon bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def process_name(m: types.Message, state: FSMContext):
    await state.update_data(user_name=m.text)
    await m.answer("Summani kiriting (Masalan: 200 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def process_amount(m: types.Message, state: FSMContext):
    await state.update_data(user_amount=m.text)
    await m.answer("Vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.time)

@dp.message(CheckState.time)
async def process_time(m: types.Message, state: FSMContext):
    user_data = await state.get_data()
    msg = await m.answer("⏳ Chek tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        # Rasm yaratish
        photo_buf = create_click_receipt_v3(user_data['user_name'], user_data['user_amount'], m.text)
        
        # Yuborish
        photo = types.BufferedInputFile(photo_buf.read(), filename="click_v3.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Marhamat, demo chek tayyor!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xatolik: {e}", reply_markup=main_menu())
    
    await state.clear()

async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
