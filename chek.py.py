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
        keyboard=[[types.KeyboardButton(text="📄 Pro Chek yaratish")]], 
        resize_keyboard=True
    )

def cancel_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

# --- Maksimal aniqlikdagi rasm chizish funksiyasi ---
def create_perfect_click_receipt(name, amount, time_str, phone_time):
    w, h = 500, 1000
    bg_color = (10, 10, 10)
    card_bg = (28, 28, 30)
    click_green = (100, 210, 80)
    click_blue = (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        # Shriftlar o'lchami (Default shrift bilan ham ishlaydi)
        f_sb = ImageFont.load_default(size=18)
        f_title = ImageFont.load_default(size=24)
        f_amount = ImageFont.load_default(size=52)
        f_name = ImageFont.load_default(size=21)
        f_reg = ImageFont.load_default(size=18)
    except:
        f_sb = f_title = f_amount = f_name = f_reg = ImageFont.load_default()

    # 1. STATUS BAR
    draw.text((45, 22), phone_time, fill="white", font=f_sb) 
    draw.rectangle([415, 24, 450, 40], outline="white", width=1)
    draw.text((385, 22), "65", fill="white", font=f_sb)

    # 2. DYNAMIC ISLAND
    draw.rounded_rectangle([180, 15, 320, 50], radius=18, fill=(0, 0, 0))
    draw.ellipse([215, 25, 230, 40], fill=click_blue)
    draw.text((235, 23), "click", fill="white")

    # 3. ASOSIY KARTA
    draw.rounded_rectangle([35, 140, 465, 550], radius=28, fill=card_bg)
    draw.rounded_rectangle([210, 105, 290, 185], radius=24, fill=click_green)
    draw.line([230, 145, 245, 160, 270, 125], fill="white", width=6)

    txt = "O'tkazma amalga oshirildi"
    tw = draw.textlength(txt, font=f_title)
    draw.text(((w - tw) / 2, 215), txt, fill=click_green, font=f_title)

    tw = draw.textlength(time_str, font=f_reg)
    draw.text(((w - tw) / 2, 260), time_str, fill=gray_text, font=f_reg)

    amt_txt = f"{amount} "
    curr_txt = "so'm"
    amt_w = draw.textlength(amt_txt, font=f_amount)
    total_w = amt_w + draw.textlength(curr_txt, font=f_name)
    start_x = (w - total_w) / 2
    draw.text((start_x, 310), amt_txt, fill="white", font=f_amount)
    draw.text((start_x + amt_w, 335), curr_txt, fill=gray_text, font=f_name)

    draw.line([65, 395, 435, 395], fill=(60, 60, 60), width=1)
    draw.rounded_rectangle([65, 420, 125, 480], radius=10, fill="white") 
    draw.text((75, 440), "click", fill=click_blue)
    
    draw.text((145, 425), name.upper(), fill="white", font=f_name)
    draw.text((145, 455), "8600 12** **** 7647", fill=gray_text, font=f_reg)

    # 4. TAYYOR TUGMASI
    draw.rounded_rectangle([45, 870, 455, 935], radius=16, fill=click_blue)
    btn_txt = "Tayyor"
    btw = draw.textlength(btn_txt, font=f_title)
    draw.text(((w - btw) / 2, 888), btn_txt, fill="white", font=f_title)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot mantiqi ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("Salom! Pro Click chek yaratish botiga xush kelibsiz.", reply_markup=main_menu())

@dp.message(F.text == "📄 Pro Chek yaratish")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting (Masalan: X. AZAMAT):", reply_markup=cancel_menu())
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
    await m.answer("3. Chek ichidagi vaqtni kiriting (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("4. Telefon tepasidagi soatni kiriting (Masalan: 08:34):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ Pro chek tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        photo_buf = create_perfect_click_receipt(data['name'], data['amount'], data['check_time'], m.text)
        photo = types.BufferedInputFile(photo_buf.read(), filename="click_pro.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ Pro Click cheki tayyor!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}", reply_markup=main_menu())
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
