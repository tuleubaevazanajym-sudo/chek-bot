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
    check_time = State()
    phone_time = State()

# --- Tugmalar ---
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📄 Click Chek yaratish")]], 
        resize_keyboard=True
    )

def cancel_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

# --- Mukammal Rasm chizish funksiyasi ---
def create_full_click_receipt(name, amount, time_str, phone_time):
    width, height = 500, 1080
    bg_color = (13, 13, 13)
    card_bg = (30, 30, 30)
    click_green = (103, 194, 58)
    click_blue = (0, 122, 255)
    gray_text = (150, 150, 150)

    img = Image.new('RGB', (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        # Shriftlar o'lchami
        f_sb = ImageFont.load_default(size=18)
        f_amt = ImageFont.load_default(size=55)
        f_st = ImageFont.load_default(size=26)
        f_nm = ImageFont.load_default(size=22)
        f_sm = ImageFont.load_default(size=18)
    except:
        f_sb = f_amt = f_st = f_nm = f_sm = ImageFont.load_default()

    # 1. TELEFON STATUS BAR
    draw.text((40, 20), phone_time, fill="white", font=f_sb) 
    draw.rectangle([420, 22, 455, 38], outline="white", width=1)
    draw.rectangle([422, 24, 445, 36], fill="white")
    draw.text((385, 20), "65", fill="white", font=f_sb)

    # 2. CLICK DYNAMIC ISLAND LOGO
    draw.rounded_rectangle([190, 15, 310, 45], radius=15, fill=(0, 0, 0))
    draw.ellipse([200, 22, 215, 37], fill=click_blue)
    draw.text((220, 20), "click", fill="white", font=f_sm)

    # 3. ASOSIY CHEK BLOKI
    draw.rounded_rectangle([30, 150, 470, 580], radius=30, fill=card_bg)
    draw.rounded_rectangle([200, 110, 300, 210], radius=35, fill=click_green)
    draw.line([225, 160, 245, 180, 275, 140], fill="white", width=8)

    draw.text((120, 250), "O'tkazma amalga oshirildi", fill=click_green, font=f_st)
    draw.text((200, 295), time_str, fill=gray_text, font=f_sm)
    draw.text((150, 340), f"{amount} so'm", fill="white", font=f_amt)

    draw.line([60, 420, 440, 420], fill=(60, 60, 60), width=1)
    draw.rounded_rectangle([60, 440, 130, 500], radius=10, fill="white") 
    draw.text((150, 445), name.upper(), fill="white", font=f_nm)
    draw.text((150, 475), "8600 12** **** 7647", fill=gray_text, font=f_sm)

    # 4. PASTDAGI TUGMA
    draw.rounded_rectangle([40, 950, 460, 1010], radius=15, fill=click_blue)
    draw.text((215, 965), "Tayyor", fill="white", font=f_st)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot mantiqi ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Mukammal Click chek yaratish botiga xush kelibsiz.", reply_markup=main_menu())

@dp.message(F.text == "📄 Click Chek yaratish")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting (Masalan: X. KAMOLA):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("2. Summani kiriting (Masalan: 30 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("3. Chek ichidagi vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("4. Telefon ekranining yuqori qismidagi soatni kiriting (Masalan: 08:34):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ Mukammal chek tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        photo_buf = create_full_click_receipt(data['name'], data['amount'], data['check_time'], m.text)
        photo = types.BufferedInputFile(photo_buf.read(), filename="click_full.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Marhamat, mukammal Click cheki!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}", reply_markup=main_menu())
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
