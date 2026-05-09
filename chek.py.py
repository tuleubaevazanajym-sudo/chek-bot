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
    card = State()
    check_time = State()
    phone_time = State()

# --- Tugmalar ---
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📱 iPhone Pro LTE Chek")]], 
        resize_keyboard=True
    )

def cancel_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

# --- Maksimal aniqlikdagi LTE rasm chizish funksiyasi ---
def create_full_pro_click_receipt(name, amount, card_num, time_str, phone_time, battery_level="88"):
    w, h = 500, 1050
    bg_color = (10, 10, 10)
    card_bg = (28, 28, 30)
    click_green = (100, 210, 80)
    click_blue = (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        f_time = ImageFont.load_default(size=18)
        f_lte = ImageFont.load_default(size=14)
        f_bat = ImageFont.load_default(size=11)
        f_title = ImageFont.load_default(size=24)
        f_amount = ImageFont.load_default(size=52)
        f_name = ImageFont.load_default(size=21)
        f_reg = ImageFont.load_default(size=18)
    except:
        f_time = f_lte = f_bat = f_title = f_amount = f_name = f_reg = ImageFont.load_default()

    # 1. STATUS BAR (Antenna va LTE bilan)
    draw.text((45, 22), phone_time, fill="white", font=f_time) 
    draw.text((310, 25), "LTE", fill="white", font=f_lte)

    # Antenna ustunlari
    for i in range(4):
        h_bars = [6, 9, 12, 15]
        color = "white" if i < 3 else (100, 100, 100)
        draw.rectangle([345 + (i*6), 39 - h_bars[i], 349 + (i*6), 39], fill=color)
    
    # Batareya quvvati
    draw.rounded_rectangle([400, 23, 445, 41], radius=5, outline=(100, 100, 100), width=1)
    draw.rectangle([445, 29, 448, 35], fill=(100, 100, 100))
    draw.rounded_rectangle([402, 25, 443, 39], radius=3, fill="white")
    draw.text((412, 26), battery_level, fill="black", font=f_bat)

    # 2. DYNAMIC ISLAND
    draw.rounded_rectangle([180, 15, 320, 48], radius=18, fill=(0, 0, 0))
    draw.ellipse([195, 22, 215, 42], fill=click_blue)
    draw.text((230, 24), "click", fill="white")

    # 3. ASOSIY CHEK BLOKI
    draw.rounded_rectangle([30, 130, 470, 500], radius=30, fill=card_bg)
    draw.rounded_rectangle([200, 95, 300, 195], radius=25, fill=click_green)
    draw.line([225, 145, 245, 165, 275, 125], fill="white", width=7)

    draw.text(((w - draw.textlength("O'tkazma amalga oshirildi", font=f_title)) / 2, 230), 
              "O'tkazma amalga oshirildi", fill=click_green, font=f_title)
    draw.text(((w - draw.textlength(time_str, font=f_reg)) / 2, 275), time_str, fill=gray_text, font=f_reg)

    # Summa
    amt_w = draw.textlength(f"{amount} ", font=f_amount)
    total_w = amt_w + draw.textlength("so'm", font=f_name)
    start_x = (w - total_w) / 2
    draw.text((start_x, 320), f"{amount} ", fill="white", font=f_amount)
    draw.text((start_x + amt_w, 345), "so'm", fill=gray_text, font=f_name)

    draw.line([60, 400, 440, 400], fill=(60, 60, 60), width=1)
    draw.rounded_rectangle([60, 420, 120, 480], radius=10, fill="white")
    draw.text((75, 445), "click", fill=click_blue)
    
    # Karta raqamini yashirish (8600 00** **** 1215)
    c = card_num.replace(" ", "")
    f_card = f"{c[:4]} {c[4:6]}** **** {c[12:]}" if len(c) == 16 else card_num

    draw.text((140, 420), name.upper(), fill="white", font=f_name)
    draw.text((140, 450), f_card, fill=gray_text, font=f_reg)

    # 4. PASTDAGI TUGMA
    draw.rounded_rectangle([40, 930, 460, 990], radius=18, fill=click_blue)
    draw.text(((w - draw.textlength("Tayyor", font=f_title)) / 2, 945), "Tayyor", fill="white", font=f_title)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot Mantiqi ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("iPhone Pro LTE Click botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📱 iPhone Pro LTE Chek")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting (Masalan: X. SOBIR):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("2. Summani kiriting (Masalan: 1 000 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("3. Karta raqamini to'liq kiriting (16 ta raqam):")
    await state.set_state(CheckState.card)

@dp.message(CheckState.card)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(card=m.text)
    await m.answer("4. Chek ichidagi vaqt (Masalan: 20 mart 8:34):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step5(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("5. Telefon soati (Masalan: 08:34):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ Pro LTE cheki tayyorlanmoqda...")
    try:
        photo_buf = create_full_pro_click_receipt(data['name'], data['amount'], data['card'], data['check_time'], m.text)
        photo = types.BufferedInputFile(photo_buf.read(), filename="click_pro_lte.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Mukammal LTE cheki tayyor!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}", reply_markup=main_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
