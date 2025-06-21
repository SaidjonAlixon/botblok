import logging
import asyncio
from aiogram import Router, F, Bot, types
from aiogram.filters import StateFilter, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, ContentType

from config import ADMIN_ID
from database import get_users_count, get_all_user_ids
from keyboards import admin_menu, back_menu, get_main_menu

admin_router = Router()

# Admin holatlari (FSM)
class AdminStates(StatesGroup):
    broadcast_message = State()
    send_to_user_id = State()
    send_to_user_message = State()
    reply_to_user = State() # Foydalanuvchiga javob yozish holati

# Admin paneliga faqat admin ID si orqali kirish
@admin_router.message(F.text == "⚙️ Admin panel", F.from_user.id == ADMIN_ID)
async def admin_panel_handler(message: Message):
    await message.answer("Siz admin panelidasiz. Kerakli bo'limni tanlang:", reply_markup=admin_menu())

# --- Admin paneli tugmalari ---

@admin_router.message(F.text == "📊 Foydalanuvchilar statistikasi", F.from_user.id == ADMIN_ID)
async def users_stats_handler(message: Message):
    count = await get_users_count()
    await message.answer(f"Botdagi jami foydalanuvchilar soni: {count} ta.")

@admin_router.message(F.text == "📢 Barchaga xabar yuborish", F.from_user.id == ADMIN_ID)
async def broadcast_handler(message: Message, state: FSMContext):
    await state.set_state(AdminStates.broadcast_message)
    await message.answer(
        "Barcha foydalanuvchilarga yuborish uchun xabar kiriting (matn, rasm, video, va hokazo).\n\n"
        "Bekor qilish uchun '⬅️ Ortga qaytish' tugmasini bosing.",
        reply_markup=back_menu
    )

@admin_router.message(F.text == "👤 ID orqali xabar", F.from_user.id == ADMIN_ID)
async def send_to_user_id_handler(message: Message, state: FSMContext):
    await state.set_state(AdminStates.send_to_user_id)
    await message.answer(
        "Xabar yuborilishi kerak bo'lgan foydalanuvchining Telegram ID sini kiriting:",
        reply_markup=back_menu
    )

@admin_router.message(F.text == "⬅️ Asosiy menyu", F.from_user.id == ADMIN_ID)
async def back_to_main_menu_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Siz asosiy menyudasiz.", reply_markup=get_main_menu(message.from_user.id))

# --- Xabar yuborish jarayonlari ---

# Barchaga xabar yuborish
@admin_router.message(StateFilter(AdminStates.broadcast_message))
async def process_broadcast(message: Message, state: FSMContext, bot: Bot):
    if message.text == "⬅️ Ortga qaytish":
        await state.clear()
        await message.answer("Admin paneliga qaytdingiz.", reply_markup=admin_menu())
        return

    await state.clear()
    await message.answer("Xabar yuborish boshlandi. Bu biroz vaqt olishi mumkin...", reply_markup=admin_menu())

    user_ids = await get_all_user_ids()
    sent_count = 0
    failed_count = 0

    for user_id in user_ids:
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            sent_count += 1
            await asyncio.sleep(0.05)  # Telegram limitlariga tushmaslik uchun
        except Exception as e:
            failed_count += 1
            logging.error(f"ID {user_id} ga xabar yuborishda xato: {e}")

    await message.answer(
        f"✅ Xabar yuborish yakunlandi!\n\n"
        f"🟢 Yuborildi: {sent_count} ta\n"
        f"🔴 Yuborilmadi (botni bloklaganlar): {failed_count} ta"
    )

# ID orqali xabar yuborish (ID ni olish)
@admin_router.message(StateFilter(AdminStates.send_to_user_id))
async def process_user_id(message: Message, state: FSMContext):
    if message.text == "⬅️ Ortga qaytish":
        await state.clear()
        await message.answer("Admin paneliga qaytdingiz.", reply_markup=admin_menu())
        return

    if not message.text.isdigit():
        await message.answer("Iltimos, faqat raqamlardan iborat to'g'ri ID kiriting.")
        return

    await state.update_data(user_id=int(message.text))
    await state.set_state(AdminStates.send_to_user_message)
    await message.answer("Endi ushbu foydalanuvchiga yuboriladigan xabarni kiriting:")

# ID orqali xabar yuborish (xabarni olish va yuborish)
@admin_router.message(StateFilter(AdminStates.send_to_user_message))
async def process_message_for_user(message: Message, state: FSMContext, bot: Bot):
    if message.text == "⬅️ Ortga qaytish":
        await state.clear()
        await message.answer("Admin paneliga qaytdingiz.", reply_markup=admin_menu())
        return

    data = await state.get_data()
    user_id = data.get('user_id')
    
    await state.clear()

    try:
        await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
        await message.answer(f"✅ ID: `{user_id}` ga xabar muvaffaqiyatli yuborildi.", parse_mode='Markdown', reply_markup=admin_menu())
    except Exception as e:
        logging.error(f"ID {user_id} ga xabar yuborishda xato: {e}")
        await message.answer(
            f"❌ ID: `{user_id}` ga xabar yuborishda xatolik yuz berdi.\\n\\n"
            f"Sabab: `{e}`",
            parse_mode='Markdown',
            reply_markup=admin_menu()
        )

# "Javob berish" tugmasi bosilganda
@admin_router.callback_query(F.data.startswith("reply_to_user:"))
async def start_reply_to_user(callback: types.CallbackQuery, state: FSMContext):
    user_id = int(callback.data.split(':')[1])
    message_id_to_reply = int(callback.data.split(':')[2])
    
    await state.set_state(AdminStates.reply_to_user)
    await state.update_data(user_id=user_id, message_id=message_id_to_reply)
    
    await callback.message.answer(
        f"✍️ Foydalanuvchiga (ID: `{user_id}`) javobingizni kiriting.\n\n"
        "Javobingiz aynan yuqoridagi xabarga 'reply' qilib yuboriladi.",
        parse_mode='Markdown'
    )
    await callback.answer()

# Admin javobini kiritganda
@admin_router.message(StateFilter(AdminStates.reply_to_user))
async def process_admin_reply(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    user_id = data.get('user_id')
    
    try:
        # 1. Foydalanuvchiga javob sarlavhasini yuborish
        await bot.send_message(user_id, "✉️ **Admin tomonidan javob:**", parse_mode='Markdown')
        
        # 2. Adminning xabarini to'liq ko'chirib yuborish
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
        await message.answer(f"✅ Javob foydalanuvchiga (ID: `{user_id}`) muvaffaqiyatli yuborildi.", parse_mode='Markdown')
    except Exception as e:
        logging.error(f"Admindan foydalanuvchiga ({user_id}) javob yuborishda xato: {e}")
        await message.answer(f"❌ Foydalanuvchiga javob yuborishda xatolik yuz berdi: {e}")
    finally:
        await state.clear() 