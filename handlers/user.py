import logging
from aiogram import Router, F, Bot, types
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, FSInputFile, CallbackQuery, WebAppInfo
from aiogram.utils.markdown import htmlescape

from config import CHANNELS, REG_CHANNEL, ADMIN_ID, WEBAPP_URL_TELEGRAM, WEBAPP_URL_SITE, SUPPORT_GROUP_URL, PARTNERSHIP_FORM_FIELDS
from database import user_exists, add_user, get_user, count_users
from keyboards import get_main_menu, get_subscribe_keyboard, back_menu, phone_request_menu

user_router = Router()

# Foydalanuvchi holatlari
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
    
    full_name_escaped = htmlescape(from_user.full_name)
    username_escaped = f"@{from_user.username}" if from_user.username else 'Mavjud emas'

    user_info_text = (
        f"{hashtag}\n\n"
        f"👤 <b>Yuboruvchi:</b> {full_name_escaped}\n"
        f"🆔 <b>ID:</b> <code>{from_user.id}</code>\n"
        f"✨ <b>Username:</b> {username_escaped}"
    )
    
    # 1. Foydalanuvchi ma'lumotlarini yuborish
    await bot.send_message(ADMIN_ID, user_info_text, parse_mode='HTML')
    
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
            return False
    return True

# Yangi foydalanuvchini bazaga qo'shish va xabar yuborish
async def register_new_user(user: types.User, bot: Bot):
    """Yangi foydalanuvchini ro'yxatdan o'tkazadi va kerakli xabarlarni yuboradi."""
    if not await user_exists(user.id):
        # Agar foydalanuvchi yangi bo'lsa, kanalga xabar yuboramiz.
        # Haqiqiy `add_user` chaqiruvi barcha ma'lumotlar to'plangandan keyin bo'ladi.
        if REG_CHANNEL:
            try:
                full_name_escaped = htmlescape(user.full_name)
                username_escaped = f"@{user.username}" if user.username else 'Mavjud emas'
                
                reg_message = (
                    f"✅ Botga yangi foydalanuvchi tashrif buyurdi (ro'yxatdan o'tishni boshladi).\n\n"
                    f"👤 Ism: {full_name_escaped}\n"
                    f"🆔 ID: <code>{user.id}</code>\n"
                    f"✍️ Username: {username_escaped}"
                )
                await bot.send_message(REG_CHANNEL, reg_message, parse_mode='HTML')
            except Exception as e:
                logging.error(f"Registratsiya kanaliga ({REG_CHANNEL}) xabar yuborishda xato: {e}")

# Asosiy menyuni yuborish funksiyasi
async def show_main_menu(message: Message, text: str):
    photo_path = 'rasmlar/welcome.jpg'
    await message.answer_photo(
        photo=FSInputFile(photo_path),
        caption=text,
        reply_markup=get_main_menu(message.from_user.id)
    )

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
        await message.answer("Assalomu alaykum! Botimizga xush kelibsiz. Ro'yxatdan o'tishni boshlaymiz.\n\nIltimos, Ism Familiya kiriting:")
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
        await callback.message.delete()
        
        if not await user_exists(callback.from_user.id):
            await callback.message.answer(
                "✅ Rahmat! Siz barcha kanallarga obuna bo'ldingiz.\n\n"
                "Endi ro'yxatdan o'tishni boshlaymiz.\n\n"
                "Iltimos, Ism Familiya kiriting:"
            )
            await state.set_state(RegistrationStates.fullname)
        else:
            photo_path = 'rasmlar/welcome.jpg'
            await callback.message.answer_photo(
                photo=FSInputFile(photo_path),
                caption="Siz asosiy menyudasiz. Kerakli bo'limni tanlang:",
                reply_markup=get_main_menu(callback.from_user.id)
            )
        
        await callback.answer()
    else:
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
    
    # Ma'lumotlarni xavfsizlash (escaping)
    full_name_escaped = htmlescape(data.get('fullname', ''))
    username_escaped = f"@{message.from_user.username}" if message.from_user.username else 'Mavjud emas'
    age_escaped = htmlescape(data.get('age', ''))
    region_escaped = htmlescape(data.get('region', ''))
    phone_escaped = htmlescape(data.get('phone', ''))
    
    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data.get('fullname'),
        age=data.get('age'),
        region=data.get('region'),
        phone=data.get('phone')
    )

    await state.clear()
    
    user_count = await count_users()

    # Admin kanaliga xabar yuborish
    try:
        if REG_CHANNEL:
            reg_message = (
                f"✅ Yangi foydalanuvchi ro'yxatdan o'tdi!\n\n"
                f"🔢 <b>Tartib raqami:</b> #{user_count}\n"
                f"👤 <b>Ism:</b> {full_name_escaped}\n"
                f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
                f"✍️ <b>Username:</b> {username_escaped}\n"
                f"🎂 <b>Yosh:</b> {age_escaped}\n"
                f"📍 <b>Manzil:</b> {region_escaped}\n"
                f"📞 <b>Telefon:</b> <code>{phone_escaped}</code>"
            )
            await bot.send_message(REG_CHANNEL, reg_message, parse_mode='HTML')
    except Exception as e:
        logging.error(f"Ro'yxatdan o'tish kanaliga ({REG_CHANNEL}) xabar yuborishda xatolik: {e}")

    await message.answer(
        "✅ Tabriklaymiz, siz muvaffaqiyatli ro'yxatdan o'tdingiz!",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_main_menu(message, "Siz asosiy menyudasiz. Kerakli bo'limni tanlang:")

@user_router.message(StateFilter(RegistrationStates.phone))
async def get_phone_text(message: Message, state: FSMContext, bot: Bot):
    # Bu funksiya agar foydalanuvchi tugmani bosmasdan, raqamini matn
    # ko'rinishida yuborsa ishlaydi.
    # Yuqoridagi get_phone funksiyasi bilan deyarli bir xil, faqat telefon
    # raqamini message.text dan oladi.
    await state.update_data(phone=message.text)
    data = await state.get_data()
    
    # Ma'lumotlarni xavfsizlash (escaping)
    full_name_escaped = htmlescape(data.get('fullname', ''))
    username_escaped = f"@{message.from_user.username}" if message.from_user.username else 'Mavjud emas'
    age_escaped = htmlescape(data.get('age', ''))
    region_escaped = htmlescape(data.get('region', ''))
    phone_escaped = htmlescape(data.get('phone', ''))

    await add_user(
        user_id=message.from_user.id,
        username=message.from_user.username,
        full_name=data.get('fullname'),
        age=data.get('age'),
        region=data.get('region'),
        phone=message.text
    )

    await state.clear()
    
    user_count = await count_users()

    # Admin kanaliga xabar yuborish
    try:
        if REG_CHANNEL:
            reg_message = (
                f"✅ Yangi foydalanuvchi ro'yxatdan o'tdi!\n\n"
                f"🔢 <b>Tartib raqami:</b> #{user_count}\n"
                f"👤 <b>Ism:</b> {full_name_escaped}\n"
                f"🆔 <b>ID:</b> <code>{message.from_user.id}</code>\n"
                f"✍️ <b>Username:</b> {username_escaped}\n"
                f"🎂 <b>Yosh:</b> {age_escaped}\n"
                f"📍 <b>Manzil:</b> {region_escaped}\n"
                f"📞 <b>Telefon:</b> <code>{phone_escaped}</code>"
            )
            await bot.send_message(REG_CHANNEL, reg_message, parse_mode='HTML')
    except Exception as e:
        logging.error(f"Ro'yxatdan o'tish kanaliga ({REG_CHANNEL}) xabar yuborishda xatolik: {e}")

    await message.answer(
        "✅ Tabriklaymiz, siz muvaffaqiyatli ro'yxatdan o'tdingiz!",
        reply_markup=ReplyKeyboardRemove()
    )
    await show_main_menu(message, "Siz asosiy menyudasiz. Kerakli bo'limni tanlang:")

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
        # Foydalanuvchi nomini to'g'ri formatlash
        username_str = f"@{user_data.get('username')}" if user_data.get('username') else "Mavjud emas"
        
        account_info = (
            f"👤 *Sizning ma'lumotlaringiz:*\n\n"
            f"🔹 *To'liq ism:* {user_data.get('full_name', 'Noma`lum')}\n"
            f"🔹 *Yosh:* {user_data.get('age', 'Noma`lum')}\n"
            f"🔹 *Manzil:* {user_data.get('region', 'Noma`lum')}\n"
            f"🔹 *Telefon:* `{user_data.get('phone', 'Noma`lum')}`\n"
            f"🔹 *Username:* {username_str}\n"
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
async def support_group_handler(message: Message):
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
        
    # Hamkorlik xabarini adminga yangi formatda yuborish
    await send_feedback_to_admin(bot, message.from_user, message, "partnership")

    await message.answer(
        "✅ Hamkorlik so'rovingiz adminga muvaffaqiyatli yuborildi. Tez orada siz bilan bog'lanamiz.",
        reply_markup=get_main_menu(message.from_user.id)
    )
    await state.clear() 