import asyncio
import io
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from PIL import Image, ImageDraw, ImageFont

# --- SOZLAMALAR ---
TOKEN = "8715924014:AAFIYd7b87EqVBmc1_hrg6g9_N92wrquv70"
KANAL_ID = "@tekinsoxtachek"
KANAL_LINK = "https://t.me/tekinsoxtachek"
ADMIN_ID = 6590911599  # Sizning ID raqamingiz

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Foydalanuvchilarni faylda saqlash tizimi
DB_FILE = "users.txt"
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: f.write("")

def add_user(user_id):
    with open(DB_FILE, "r") as f:
        users = f.read().splitlines()
    if str(user_id) not in users:
        with open(DB_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_users_count():
    with open(DB_FILE, "r") as f:
        return len(f.read().splitlines())

class CheckState(StatesGroup):
    name = State()
    amount = State()
    card = State()
    check_time = State()
    phone_time = State()

# --- OBUNANI TEKSHIRISH ---
async def check_sub(user_id):
    try:
        member = await bot.get_chat_member(chat_id=KANAL_ID, user_id=user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# --- TUGMALAR ---
def main_menu(user_id):
    kb = [[types.KeyboardButton(text="📱 iPhone Pro Click")]]
    if user_id == ADMIN_ID:
        kb.append([types.KeyboardButton(text="📊 Statistika")])
    return types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def sub_inline():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Obuna bo'lish", url=KANAL_LINK)],
        [InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_sub")]
    ])

# --- Rasm Chizish Funksiyasi (Mukammal Dizayn) ---
def create_final_click_receipt(name, amount, card_num, time_str, phone_time):
    w, h = 500, 1050
    bg_color, card_bg = (10, 10, 10), (28, 28, 30)
    click_green, click_blue = (100, 210, 80), (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        f_time = ImageFont.load_default(size=18)
        f_lte = ImageFont.load_default(size=14)
        f_bat = ImageFont.load_default(size=11)
        f_amt = ImageFont.load_default(size=52)
        f_nm = ImageFont.load_default(size=21)
        f_reg = ImageFont.load_default(size=18)
        f_bold = ImageFont.load_default(size=24)
    except:
        f_time = f_lte = f_bat = f_amt = f_nm = f_reg = f_bold = ImageFont.load_default()

    # Status Bar
    draw.text((45, 25), phone_time, fill="white", font=f_time)
    draw.text((330, 27), "LTE", fill="white", font=f_lte)
    # Antenna
    for i in range(4):
        heights = [5, 8, 11, 14]
        color = "white" if i < 3 else (80, 80, 80)
        draw.rectangle([365 + (i*6), 40 - heights[i], 369 + (i*6), 40], fill=color)
    # Batareya
    draw.rounded_rectangle([400, 23, 435, 41], radius=4, outline=(150, 150, 150))
    draw.rectangle([435, 28, 438, 36], fill=(150, 150, 150))
    draw.rounded_rectangle([402, 25, 433, 39], radius=2, fill="white")
    draw.text((410, 27), "88", fill="black", font=f_bat)

    # Dynamic Island
    draw.rounded_rectangle([180, 15, 320, 48], radius=18, fill=(0, 0, 0))
    draw.ellipse([195, 24, 212, 41], fill=click_blue)
    draw.text((225, 24), "click", fill="white")

    # Chek Blok
    draw.rounded_rectangle([30, 130, 470, 520], radius=30, fill=card_bg)
    draw.rounded_rectangle([200, 95, 300, 195], radius=25, fill=click_green)
    draw.line([225, 145, 245, 165, 275, 125], fill="white", width=7)

    draw.text(((w - draw.textlength("O'tkazma amalga oshirildi", font=f_bold)) / 2, 230), 
              "O'tkazma amalga oshirildi", fill=click_green, font=f_bold)
    draw.text(((w - draw.textlength(time_str, font=f_reg)) / 2, 275), time_str, fill=gray_text, font=f_reg)
    
    amt_w = draw.textlength(f"{amount} ", font=f_amt)
    start_x = (w - (amt_w + draw.textlength("so'm", font=f_reg))) / 2
    draw.text((start_x, 320), f"{amount} ", fill="white", font=f_amt)
    draw.text((start_x + amt_w, 345), "so'm", fill=gray_text, font=f_reg)

    draw.line([60, 410, 440, 410], fill=(60, 60, 60), width=1)
    draw.rounded_rectangle([60, 430, 120, 490], radius=10, fill="white")
    
    c = card_num.replace(" ", "")
    f_c = f"{c[:4]} {c[4:6]}** **** {c[12:]}" if len(c) == 16 else card_num
    draw.text((140, 430), name.upper(), fill="white", font=f_nm)
    draw.text((140, 460), f_c, fill=gray_text, font=f_reg)

    # Tugma
    draw.rounded_rectangle([40, 930, 460, 990], radius=20, fill=click_blue)
    draw.text(((w - draw.textlength("Tayyor", font=f_nm)) / 2, 945), "Tayyor", fill="white", font=f_nm)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- BOT INTERAKSIYASI ---
@dp.message(Command("start"))
async def cmd_start(m: types.Message):
    add_user(m.from_user.id)
    if await check_sub(m.from_user.id):
        await m.answer(f"Xush kelibsiz, {m.from_user.first_name}!", reply_markup=main_menu(m.from_user.id))
    else:
        await m.answer("⚠️ Botdan foydalanish uchun kanalga obuna bo'ling!", reply_markup=sub_inline())

@dp.message(F.text == "📊 Statistika")
async def show_stats(m: types.Message):
    if m.from_user.id == ADMIN_ID:
        count = get_users_count()
        await m.answer(f"📊 **Bot statistikasi:**\n\n👤 Foydalanuvchilar: {count} ta", parse_mode="Markdown")

@dp.callback_query(F.data == "check_sub")
async def check_callback(call: types.CallbackQuery):
    if await check_sub(call.from_user.id):
        await call.message.delete()
        await call.message.answer("✅ Obuna tasdiqlandi!", reply_markup=main_menu(call.from_user.id))
    else:
        await call.answer("❌ Hali obuna bo'lmagansiz!", show_alert=True)

@dp.message(F.text == "📱 iPhone Pro Click")
async def step1(m: types.Message, state: FSMContext):
    if not await check_sub(m.from_user.id): return await m.answer("Avval obuna bo'ling!", reply_markup=sub_inline())
    await m.answer("1. Ism familiya (Masalan: X. AXMAT):", reply_markup=types.ReplyKeyboardRemove())
    await state.set_state(CheckState.name)

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(n=m.text); await m.answer("2. Summa:"); await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(a=m.text); await m.answer("3. Karta raqami (16 ta):"); await state.set_state(CheckState.card)

@dp.message(CheckState.card)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(c=m.text); await m.answer("4. Chek vaqti:"); await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step5(m: types.Message, state: FSMContext):
    await state.update_data(ct=m.text); await m.answer("5. Telefon soati:"); await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    d = await state.get_data()
    msg = await m.answer("⏳ Tayyorlanmoqda...")
    try:
        buf = create_final_click_receipt(d['n'], d['a'], d['c'], d['ct'], m.text)
        await bot.send_photo(m.chat.id, types.BufferedInputFile(buf.read(), filename="res.png"), reply_markup=main_menu(m.from_user.id))
        await msg.delete()
    except Exception as e: await m.answer(f"Xato: {e}")
    await state.clear()

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
