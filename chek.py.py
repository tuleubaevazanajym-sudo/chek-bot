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
    card = State()      # Karta raqami uchun yangi bosqich
    check_time = State()
    phone_time = State()

# --- Tugmalar ---
def main_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="📱 iPhone Click Chek")]], 
        resize_keyboard=True
    )

def cancel_menu():
    return types.ReplyKeyboardMarkup(
        keyboard=[[types.KeyboardButton(text="❌ Bekor qilish")]], 
        resize_keyboard=True
    )

# --- iPhone Dizaynidagi Rasm Chizish Funksiyasi ---
def create_iphone_click_receipt(name, amount, card_num, time_str, phone_time):
    w, h = 500, 1080
    bg_color = (10, 10, 10)
    card_bg = (28, 28, 30)
    click_green = (100, 210, 80)
    click_blue = (0, 122, 255)
    gray_text = (142, 142, 147)

    img = Image.new('RGB', (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    try:
        # Shriftlar o'lchami
        f_sb = ImageFont.load_default(size=19)
        f_title = ImageFont.load_default(size=25)
        f_amount = ImageFont.load_default(size=56)
        f_name = ImageFont.load_default(size=22)
        f_reg = ImageFont.load_default(size=19)
    except:
        f_sb = f_title = f_amount = f_name = f_reg = ImageFont.load_default()

    # 1. iPhone Status Bar (Soat va Ikonalar)
    draw.text((45, 25), phone_time, fill="white", font=f_sb) 
    # Batareya simvoli
    draw.rectangle([415, 27, 455, 43], outline="white", width=1)
    draw.rectangle([417, 29, 440, 41], fill="white")
    draw.text((380, 25), "88", fill="white", font=f_sb)

    # 2. Dynamic Island (iPhone 14/15 Pro uslubi)
    draw.rounded_rectangle([180, 18, 320, 52], radius=17, fill=(0, 0, 0))
    draw.ellipse([195, 28, 210, 43], fill=click_blue) # Click kichik nuqtasi
    draw.text((220, 26), "click", fill="white")

    # 3. Asosiy Chek Bloki (Card)
    draw.rounded_rectangle([35, 160, 465, 620], radius=35, fill=card_bg)
    
    # Yashil Galochka (Yumaloq)
    draw.rounded_rectangle([210, 120, 290, 200], radius=28, fill=click_green)
    draw.line([235, 160, 245, 175, 270, 145], fill="white", width=7)

    # Matn: Muvaffaqiyatli o'tkazma
    txt = "O'tkazma amalga oshirildi"
    tw = draw.textlength(txt, font=f_title)
    draw.text(((w - tw) / 2, 245), txt, fill=click_green, font=f_title)

    # Matn: Sana va vaqt
    tw = draw.textlength(time_str, font=f_reg)
    draw.text(((w - tw) / 2, 295), time_str, fill=gray_text, font=f_reg)

    # Summa
    amt_txt = f"{amount} "
    curr_txt = "so'm"
    amt_w = draw.textlength(amt_txt, font=f_amount)
    total_w = amt_w + draw.textlength(curr_txt, font=f_name)
    start_x = (w - total_w) / 2
    draw.text((start_x, 345), amt_txt, fill="white", font=f_amount)
    draw.text((start_x + amt_w, 375), curr_txt, fill=gray_text, font=f_name)

    # Ajratuvchi nuqtali chiziq
    draw.line([70, 440, 430, 440], fill=(60, 60, 60), width=1)

    # Karta va Ism qismi
    draw.rounded_rectangle([70, 470, 135, 535], radius=12, fill="white") # Oq karta foni
    draw.text((82, 495), "click", fill=click_blue)
    
    draw.text((155, 475), name.upper(), fill="white", font=f_name)
    draw.text((155, 510), card_num, fill=gray_text, font=f_reg) # Foydalanuvchi kiritgan karta

    # 4. Pastdagi "Tayyor" Tugmasi
    draw.rounded_rectangle([40, 960, 460, 1030], radius=20, fill=click_blue)
    btn_txt = "Tayyor"
    btw = draw.textlength(btn_txt, font=f_title)
    draw.text(((w - btw) / 2, 978), btn_txt, fill="white", font=f_title)

    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

# --- Bot Mantiqi ---
@dp.message(Command("start"))
async def start(m: types.Message):
    await m.answer("iPhone dizaynidagi Click botga xush kelibsiz!", reply_markup=main_menu())

@dp.message(F.text == "📱 iPhone Click Chek")
async def step1(m: types.Message, state: FSMContext):
    await m.answer("1. Ism familiyani kiriting:", reply_markup=cancel_menu())
    await state.set_state(CheckState.name)

@dp.message(F.text == "❌ Bekor qilish")
async def cancel(m: types.Message, state: FSMContext):
    await state.clear()
    await m.answer("Bekor qilindi.", reply_markup=main_menu())

@dp.message(CheckState.name)
async def step2(m: types.Message, state: FSMContext):
    await state.update_data(name=m.text)
    await m.answer("2. Summani kiriting (Masalan: 500 000):")
    await state.set_state(CheckState.amount)

@dp.message(CheckState.amount)
async def step3(m: types.Message, state: FSMContext):
    await state.update_data(amount=m.text)
    await m.answer("3. Karta raqamini kiriting (Masalan: 8600 00** **** 1234):")
    await state.set_state(CheckState.card)

@dp.message(CheckState.card)
async def step4(m: types.Message, state: FSMContext):
    await state.update_data(card=m.text)
    await m.answer("4. Chek ichidagi vaqt (Masalan: 20 mar 8:34):")
    await state.set_state(CheckState.check_time)

@dp.message(CheckState.check_time)
async def step5(m: types.Message, state: FSMContext):
    await state.update_data(check_time=m.text)
    await m.answer("5. Telefon tepasidagi soat (Masalan: 08:34):")
    await state.set_state(CheckState.phone_time)

@dp.message(CheckState.phone_time)
async def final(m: types.Message, state: FSMContext):
    data = await state.get_data()
    msg = await m.answer("⏳ iPhone dizaynida chek tayyorlanmoqda...", reply_markup=types.ReplyKeyboardRemove())
    
    try:
        photo_buf = create_iphone_click_receipt(
            data['name'], data['amount'], data['card'], data['check_time'], m.text
        )
        photo = types.BufferedInputFile(photo_buf.read(), filename="iphone_click.png")
        await bot.send_photo(m.chat.id, photo, caption="✅ iPhone Click cheki tayyor!", reply_markup=main_menu())
        await msg.delete()
    except Exception as e:
        await m.answer(f"Xato: {e}", reply_markup=main_menu())
    
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
