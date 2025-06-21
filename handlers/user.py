import logging
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, CallbackQuery, WebAppInfo

from config import CHANNELS, REG_CHANNEL, ADMIN_ID, WEBAPP_URL_TELEGRAM, WEBAPP_URL_SITE, SUPPORT_GROUP_URL, PARTNERSHIP_FORM_FIELDS
from database import user_exists, add_user, get_user
from keyboards import get_main_menu, get_subscribe_keyboard, back_menu, phone_request_menu

user_router = Router()

# Foydalanuvchi holatlari (FSM)
class RegistrationStates(StatesGroup):
    fullname = State()
    age = State()
    region = State()
    phone = State()

class PartnershipState(StatesGroup):
    form_data = State()

class AppealState(StatesGroup):
    message_to_admin = State()

async def send_feedback_to_admin(bot: Bot, from_user: types.User, message: types.Message, feedback_type: str):
    """Murojaat/hamkorlik haqidagi ma'lumotni adminga formatlab yuboradi."""
    hashtag = "#Murojaat" if feedback_type == "appeal" else "#Hamkorlik"
    
    user_info_text = (
        f"{hashtag}\n\n"
        f"👤 **Yuboruvchi:** {from_user.full_name}\n"
        f"🆔 **ID:** `{from_user.id}`\n"
        f"✨ **Username:** @{from_user.username if from_user.username else 'Mavjud emas'}"
    )
    
    # 1. Foydalanuvchi ma'lumotlarini yuborish
    await bot.send_message(ADMIN_ID, user_info_text, parse_mode='Markdown')
    
    # 2. Asosiy xabarni forward qilish
    forwarded_message = await bot.forward_message(
        chat_id=ADMIN_ID,
        from_chat_id=message.chat.id,
        message_id=message.message_id
    )
    
    # 3. Javob berish tugmasini yuborish
    reply_kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="💬 Javob berish", callback_data=f"reply_to_user:{from_user.id}:{forwarded_message.message_id}")]
    ])
    
    await bot.send_message(
        ADMIN_ID,
        "Foydalanuvchiga javob berish uchun tugmani bosing:",
        reply_markup=reply_kb
    )

# Majburiy obunani tekshiruvchi funksiya
async def check_subscription(user_id: int, bot: Bot):
    for channel in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status not in ['member', 'administrator', 'creator']:
                return False
        except Exception as e:
            logging.error(f"Kanalni tekshirishda xato ({channel}): {e}")
            return False  # Agar kanal topilmasa yoki boshqa xatolik bo'lsa
    return True

# /start buyrug'i uchun handler
@user_router.message(CommandStart())
async def start_handler(message: Message, bot: Bot, state: FSMContext):
    await state.clear()
    if not await check_subscription(message.from_user.id, bot):
        await message.answer(
            "Assalomu alaykum! Botdan foydalanish uchun, iltimos, quyidagi kanallarimizga obuna bo'ling:",
            reply_markup=get_subscribe_keyboard()
        )
        return

    if not await user_exists(message.from_user.id):
        await message.answer("Assalomu alaykum! Botimizga xush kelibsiz. Ro'yxatdan o'tishni boshlaymiz.\n\nIltimos, to'liq ism-sharifingizni kiriting:")
        await state.set_state(RegistrationStates.fullname)
    else:
        photo_path = 'rasmlar/welcome.jpg'
        await message.answer_photo(
            photo=FSInputFile(photo_path),
            caption="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
            reply_markup=get_main_menu(message.from_user.id)
        )

# Obunani tekshirish tugmasi uchun handler
@user_router.callback_query(F.data == "check_subs")
async def check_subs_callback(callback: types.CallbackQuery, bot: Bot, state: FSMContext):
    if await check_subscription(callback.from_user.id, bot):
        # Obuna tasdiqlandi, eski xabarni o'chiramiz
        await callback.message.delete()
        
        # Foydalanuvchi bazada bor-yo'qligini tekshiramiz
        if not await user_exists(callback.from_user.id):
            # Agar yo'q bo'lsa, ro'yxatdan o'tishni boshlaymiz
            await callback.message.answer(
                "✅ Rahmat! Siz barcha kanallarga obuna bo'ldingiz.\n\n"
                "Endi ro'yxatdan o'tishni boshlaymiz.\n\n"
                "Iltimos, to'liq ism-sharifingizni kiriting:"
            )
            await state.set_state(RegistrationStates.fullname)
        else:
            # Agar bazada mavjud bo'lsa, asosiy menyuni ko'rsatamiz
            photo_path = 'rasmlar/welcome.jpg'
            await callback.message.answer_photo(
                photo=FSInputFile(photo_path),
                caption="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
                reply_markup=get_main_menu(callback.from_user.id)
            )
        
        await callback.answer() # Callbackga javob qaytaramiz
    else:
        # Agar obuna to'liq bo'lmasa
        await callback.answer("Siz hali barcha kanallarga obuna bo'lmadingiz.", show_alert=True)

# --- Ro'yxatdan o'tish jarayoni ---

@user_router.message(StateFilter(RegistrationStates.fullname))
async def get_fullname(message: Message, state: FSMContext):
    await state.update_data(fullname=message.text)
    await message.answer("Yoshingizni kiriting:")
    await state.set_state(RegistrationStates.age)

@user_router.message(StateFilter(RegistrationStates.age))
async def get_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer("Yashash manzilingizni kiriting (viloyat/shahar):")
    await state.set_state(RegistrationStates.region)

@user_router.message(StateFilter(RegistrationStates.region))
async def get_region(message: Message, state: FSMContext):
    await state.update_data(region=message.text)
    await message.answer("Telefon raqamingizni yuboring:", reply_markup=phone_request_menu)
    await state.set_state(RegistrationStates.phone)

@user_router.message(StateFilter(RegistrationStates.phone), F.contact)
async def get_phone(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(phone=message.contact.phone_number)
    data = await state.get_data()
    
    user_id = message.from_user.id
    fullname = data.get('fullname')
    age = data.get('age')
    region = data.get('region')
    phone = data.get('phone')
    username = message.from_user.username

    user_number = await add_user(user_id, fullname, age, region, phone, username)

    await state.clear()

    # Admin kanaliga xabar yuborish
    try:
        if REG_CHANNEL:
            reg_message = (
                f"✅ Yangi foydalanuvchi ro'yxatdan o'tdi!\n\n"
                f"🔢 Tartib raqami: #{user_number}\n"
                f"👤 Ism: {fullname}\n"
                f"🆔 ID: `{user_id}`\n"
                f"✍️ Username: @{username if username else 'Mavjud emas'}\n"
                f"🎂 Yosh: {age}\n"
                f"📍 Manzil: {region}\n"
                f"📞 Telefon: `{phone}`"
            )
            await bot.send_message(REG_CHANNEL, reg_message, parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Registratsiya kanaliga ({REG_CHANNEL}) xabar yuborishda xato: {e}")

    photo_path = 'rasmlar/welcome.jpg'
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=f"Tabriklaymiz, siz muvaffaqiyatli ro'yxatdan o'tdingiz!\n\nSiz asosiy menyudasiz. Kerakli bo'limni tanlang:",
        reply_markup=get_main_menu(message.from_user.id)
    )

# --- Asosiy menyu tugmalari ---

@user_router.message(F.text == "📝 Blok test ishlash")
async def block_test_handler(message: Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🚀 Testni boshlash", web_app=WebAppInfo(url=WEBAPP_URL_TELEGRAM))],
            [types.InlineKeyboardButton(text="📖 Yo'riqnoma", url=WEBAPP_URL_SITE)]
        ]
    )
    await message.answer("Blok test ishlash uchun quyidagi tugmani bosing:", reply_markup=keyboard)

@user_router.message(F.text == "👤 Mening hisobim")
async def my_account_handler(message: Message):
    user_data = await get_user(message.from_user.id)
    if user_data:
        account_info = (
            f"👤 *Sizning ma'lumotlaringiz:*\n\n"
            f"🔹 *Ism-sharif:* {user_data.get('fullname', 'Noma`lum')}\n"
            f"🔹 *Yosh:* {user_data.get('age', 'Noma`lum')}\n"
            f"🔹 *Manzil:* {user_data.get('region', 'Noma`lum')}\n"
            f"🔹 *Telefon:* `{user_data.get('phone', 'Noma`lum')}`\n"
            f"🔹 *Telegram ID:* `{message.from_user.id}`"
        )
        await message.answer(account_info, parse_mode='Markdown')
    else:
        await message.answer("Siz haqingizda ma'lumot topilmadi. Qayta ro'yxatdan o'tish uchun /start bosing.")

@user_router.message(F.text == "📨 Aloqa va murojaat")
async def contact_handler(message: Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✍️ Murojaat yuborish", callback_data="send_appeal_application")]
        ]
    )
    await message.answer(
        "Adminga murojaat yuborish uchun quyidagi tugmani bosing.",
        reply_markup=keyboard
    )

@user_router.callback_query(F.data == "send_appeal_application")
async def send_appeal_application_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "✍️ Adminga yuborish uchun murojaatingizni shu yerga yozing (matn, rasm, video...).\n\n"
        "Murojaatingiz to'g'ridan-to'g'ri adminga yuboriladi.",
        reply_markup=back_menu
    )
    await state.set_state(AppealState.message_to_admin)
    await callback.answer()

@user_router.message(StateFilter(AppealState.message_to_admin))
async def process_appeal_message(message: Message, state: FSMContext, bot: Bot):
    if message.text == "⬅️ Ortga qaytish":
        await state.clear()
        await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu(message.from_user.id))
        return

    # Murojaatni adminga yangi formatda yuborish
    await send_feedback_to_admin(bot, message.from_user, message, "appeal")

    await message.answer(
        "✅ Murojaatingiz adminga muvaffaqiyatli yuborildi. Tez orada javob olasiz.",
        reply_markup=get_main_menu(message.from_user.id)
    )
    await state.clear()

@user_router.message(F.text == "👥 Qo'llab quvvatlash guruhi")
async def support_handler(message: Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[[types.InlineKeyboardButton(text="Guruhga o'tish", url=SUPPORT_GROUP_URL)]]
    )
    await message.answer("Texnik yordam va savol-javoblar uchun qo'llab-quvvatlash guruhimizga qo'shiling:", reply_markup=keyboard)

@user_router.message(F.text == "🤝 Hamkorlik")
async def partnership_handler(message: Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="✍️ Ariza yuborish", callback_data="send_partnership_application")]
        ]
    )
    await message.answer(
        "🤝 O'quv markazingiz bilan hamkorlik qilishdan mamnun bo'lamiz!\n\n"
        "Bizning saytni o'quv markazingizda qo'llang va zamonaviy yechimlar hamda qulayliklarga ega bo'ling!\n\n"
        "Ariza yuborish uchun tugmani bosing.",
        reply_markup=keyboard
    )

@user_router.callback_query(F.data == "send_partnership_application")
async def send_partnership_application_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Hamkorlik bo'yicha taklifingizni yoki arizangizni shu yerga yuboring (matn, rasm, fayl...):",
        reply_markup=back_menu
    )
    await state.set_state(PartnershipState.form_data)
    await callback.answer()

@user_router.message(StateFilter(PartnershipState.form_data))
async def process_partnership_message(message: Message, state: FSMContext, bot: Bot):
    if message.text == "⬅️ Ortga qaytish":
        await state.clear()
        await message.answer("Asosiy menyuga qaytdingiz.", reply_markup=get_main_menu(message.from_user.id))
        return

    # Hamkorlik arizasini adminga yangi formatda yuborish
    await send_feedback_to_admin(bot, message.from_user, message, "partnership")

    await message.answer(
        "✅ Hamkorlik bo'yicha arizangiz adminga muvaffaqiyatli yuborildi.",
        reply_markup=get_main_menu(message.from_user.id)
    )
    await state.clear() 