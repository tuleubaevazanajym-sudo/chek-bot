import asyncio
import io
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from PIL import Image, ImageDraw, ImageFont

TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class CheckState(StatesGroup):
    name = State()
    amount = State()
    card = State()
    check_time = State()
    phone_time = State()

def main_menu():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="📱 Click Real iPhone")]], resize_keyboard=True)

def cancel_menu():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

def create_real_iphone_receipt(name, amount, card_num, time_str, phone_time, battery_level="88"):
    w, h = 500, 1000
    bg_color = (10, 10, 10)
    card_bg = (28, 28, 30)
    click_green = (100, 210, 80)
    click_blue = (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        f_time = ImageFont.load_default(size=18)
        f_lte = ImageFont.load_default(size=13)
        f_bat = ImageFont.load_default(size=10) # Batareya raqami kichikroq
        f_amt = ImageFont.load_default(size=52)
        f_nm = ImageFont.load_default(size=21)
        f_reg = ImageFont.load_default(size=18)
        f_bold = ImageFont.load_default(size=24)
    except:
        f_time = f_lte = f_bat = f_amt = f_nm = f_reg = f_bold = ImageFont.load_default()

    # 1. STATUS BAR (Haqiqiy iPhone o'lchamlari)
    draw.text((45, 22), phone_time, fill="white", font=f_time) # Soat

    # --- Batareya (Kichraytirildi: 415-445 gacha, jami 30 piksel) ---
    draw.rounded_rectangle([415, 23, 445, 38], radius=4, outline=(150, 150, 150), width=1)
    draw.rectangle([445, 28, 447, 33], fill=(150, 150, 150)) # Burun qismi
    draw.rounded_rectangle([417, 25, 443, 36], radius=2, fill="white") # Quvvat darajasi
    
    # Batareya ichidagi raqam
    draw.text((420, 25), battery_level, fill="black", font=f_bat)

    # --- Tarmoq Antennasi (Batareyaga yaqinroq) ---
    for i in range(4):
        heights = [5, 8, 11, 14]
        color = "white" if i < 3 else (80, 80, 80)
        draw.rectangle([385 + (i*6), 38 - heights[i], 389 + (i*6), 38], fill=color)

    # --- LTE yozuvi ---
    draw.text((355, 25), "LTE", fill="white", font=f_lte)

    # 2. DYNAMIC ISLAND
    draw.rounded_rectangle([180, 15, 320, 48], radius=18, fill=(0, 0, 0))
    draw.ellipse([195, 22, 215, 42], fill=click_blue)
    draw.text((230, 24), "click", fill="white")

    # 3. ASOSIY CHEK
    draw.rounded_rectangle([30, 130, 470, 500], radius=30, fill=card_bg)
    draw.rounded_rectangle([200, 95, 300, 195], radius=25, fill=click_green)
    draw.line([225, 145, 245, 165, 275, 125], fill="white", width=7)

    draw.text(((w - draw.textlength("O'tkazma amalga oshirildi", font=f_bold)) / 2, 230), 
              "O'tkazma amalga oshirildi", fill=click_green, font=f_bold)
    draw.text(((w - draw.textlength(time_str, font=f_reg)) / 2, 275), time_str, fill=gray_text, font=f_reg)

    amt_w = draw.textlength(f"{amount} ", font=f_amt)
    total_w = amt_w + draw.textlength("so'm", font=f_reg)
    start_x = (w - total_w) / 2
    draw.text((start_x, 320), f"{amount} ", fill="white", font=f_amt)
    draw.text((start_x + amt_w, 345), "so'm", fill=gray_text, font=f_reg)

    draw.line([60, 400, 440, 400], fill=(60, 60, 60), width=1)
    draw.rounded_rectangle([60, 420, 120, 480], radius=10, fill="white")
    
    c = card_num.replace(" ", "")
    f_card = f"{c[:4]} {c[4:6]}** **** {c[12:]}" if len(c) == 16 else card_num

    draw.text((140, 420), name.upper(), fill="white", font=f_nm)
    draw.text((140, 450), f_card, fill=gray_text, font=f_reg)

    # 4. TAYYOR TUGMASI
    draw.rounded_rectangle([40, 900, 460, 960], radius=18, fill=click_blue)
    draw.text(((w - draw.textlength("Tayyor", font=f_nm)) / 2, 915), "Tayyor", fill="white", font=f_nm)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot mantiqi yuqoridagidek qoladi ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("📱 Real iPhone Click botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📱 Click Real iPhone")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting (Masalan: X. AXMAT):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("2. Summani kiriting (Masalan: 1 111 999):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("3. Karta raqamini to'liq kiriting (16 ta raqam):")
    await state.set_state(CheckState.card)

@dp.message(CheckState.card)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(card=m.text)
    await m.answer("4. Chek ichidagi vaqt (Masalan: 20 mart 21:14):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step5(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("5. Telefon soati (Masalan: 21:14):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ Real iPhone cheki tayyorlanmoqda...")
    try:
        photo_buf = create_real_iphone_receipt(data['name'], data['amount'], data['card'], data['check_time'], m.text)
        photo = types.BufferedInputFile(photo_buf.read(), filename="iphone_real.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ iPhone batareyasi va ikonkalari to'g'rilangan chek!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
