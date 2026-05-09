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
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="📱 iPhone Click Chek")]], resize_keyboard=True)

def cancel_menu():
    return types.ReplyKeyboardMarkup(keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], resize_keyboard=True)

def create_iphone_pro_receipt(name, amount, card_num, time_str, phone_time):
    w, h = 500, 1080
    bg_color = (10, 10, 10)
    card_bg = (28, 28, 30)
    click_green = (100, 210, 80)
    click_blue = (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        f_sb = ImageFont.load_default(size=18)
        f_title = ImageFont.load_default(size=24)
        f_amount = ImageFont.load_default(size=54)
        f_name = ImageFont.load_default(size=22)
        f_reg = ImageFont.load_default(size=18)
    except:
        f_sb = f_title = f_amount = f_name = f_reg = ImageFont.load_default()

    # 1. IPHONE STATUS BAR (Antenna, Wi-Fi, Batareya)
    draw.text((40, 25), phone_time, fill="white", font=f_sb) # Soat
    
    # Antenna (4 ta ustuncha)
    draw.rectangle([345, 38, 348, 42], fill="white")
    draw.rectangle([351, 34, 354, 42], fill="white")
    draw.rectangle([357, 30, 360, 42], fill="white")
    draw.rectangle([363, 26, 366, 42], fill="gray") # Oxirgisi biroz xira

    # Wi-Fi belgisi (Simvol)
    draw.text((375, 25), "📶", fill="white", font=f_sb)

    # Batareya
    draw.rectangle([425, 26, 460, 42], outline="white", width=1)
    draw.rectangle([427, 28, 452, 40], fill="white")
    draw.text((400, 25), "88", fill="white", font=f_sb)

    # 2. DYNAMIC ISLAND
    draw.rounded_rectangle([190, 18, 310, 52], radius=17, fill=(0, 0, 0))
    draw.ellipse([205, 28, 215, 38], fill=click_blue)
    draw.text((225, 26), "click", fill="white")

    # 3. ASOSIY KARTA
    draw.rounded_rectangle([35, 140, 465, 530], radius=32, fill=card_bg)
    draw.rounded_rectangle([205, 100, 295, 190], radius=28, fill=click_green)
    draw.line([225, 145, 245, 165, 275, 125], fill="white", width=7)

    txt = "O'tkazma amalga oshirildi"
    tw = draw.textlength(txt, font=f_title)
    draw.text(((w - tw) / 2, 235), txt, fill=click_green, font=f_title)
    
    tw = draw.textlength(time_str, font=f_reg)
    draw.text(((w - tw) / 2, 280), time_str, fill=gray_text, font=f_reg)

    # Summa (400 000 so'm)
    amt_w = draw.textlength(f"{amount} ", font=f_amount)
    total_w = amt_w + draw.textlength("so'm", font=f_name)
    start_x = (w - total_w) / 2
    draw.text((start_x, 330), f"{amount} ", fill="white", font=f_amount)
    draw.text((start_x + amt_w, 355), "so'm", fill=gray_text, font=f_name)

    draw.line([65, 415, 435, 415], fill=(60, 60, 60), width=1)

    # Karta va Foydalanuvchi ma'lumotlari
    draw.rounded_rectangle([65, 440, 125, 500], radius=10, fill="white")
    draw.text((72, 460), "click", fill=click_blue)

    # Karta raqamini formatlash (8600 00** **** 1234)
    card_parts = card_num.replace(" ", "")
    if len(card_parts) == 16:
        formatted_card = f"{card_parts[:4]} {card_parts[4:6]}** **** {card_parts[12:]}"
    else:
        formatted_card = card_num # Agar noto'g'ri kiritilsa o'zi qoladi

    draw.text((145, 440), name.upper(), fill="white", font=f_name)
    draw.text((145, 475), formatted_card, fill=gray_text, font=f_reg)

    # 4. TAYYOR TUGMASI
    draw.rounded_rectangle([40, 950, 460, 1010], radius=20, fill=click_blue)
    btw = draw.textlength("Tayyor", font=f_title)
    draw.text(((w - btw) / 2, 968), "Tayyor", fill="white", font=f_title)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("iPhone Pro Click botiga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📱 iPhone Click Chek")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting (Masalan: X AZAMAT):", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("2. Summani kiriting (Masalan: 200 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("3. Karta raqamini to'liq kiriting (16 ta raqam):\nBot o'zi o'rtasini **** qilib beradi.")
    await state.set_state(CheckState.card)

@dp.message(CheckState.card)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(card=m.text)
    await m.answer("4. Chek ichidagi vaqt (Masalan: 20 mart 8:34):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step5(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("5. Telefon soati (Masalan: 8:34):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ iPhone Pro dizaynida chek tayyorlanmoqda...")
    try:
        photo_buf = create_iphone_pro_receipt(data['name'], data['amount'], data['card'], data['check_time'], m.text)
        photo = types.BufferedInputFile(photo_buf.read(), filename="iphone_pro.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Marhamat, iPhone Pro cheki!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}", reply_markup=main_menu())
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
