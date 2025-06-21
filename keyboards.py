from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import CHANNELS, ADMIN_ID

# ==================== ODDIY FOYDALANUVCHI UCHUN KLAVIATURALAR ====================

def get_main_menu(user_id: int):
    """Foydalanuvchi ID siga qarab asosiy menyuni qaytaradi (admin/oddiy)."""
    keyboard = [
        [KeyboardButton(text="📝 Blok test ishlash")],
        [KeyboardButton(text="👤 Mening hisobim"), KeyboardButton(text="📨 Aloqa va murojaat")],
        [KeyboardButton(text="👥 Qo'llab quvvatlash guruhi"), KeyboardButton(text="🤝 Hamkorlik")]
    ]
    if user_id == ADMIN_ID:
        keyboard.append([KeyboardButton(text="⚙️ Admin panel")])
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)

def get_subscribe_keyboard():
    """Majburiy obuna kanallari uchun inline klaviatura."""
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"➕ {channel.lstrip('@')}", url=f"https://t.me/{channel.lstrip('@')}")]
        for channel in CHANNELS
    ])
    kb.inline_keyboard.append([InlineKeyboardButton(text="✅ Tekshirish", callback_data="check_subs")])
    return kb

# Ortga qaytish tugmasi
back_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="⬅️ Ortga qaytish")]], 
    resize_keyboard=True
)

# Telefon raqamni yuborish tugmasi
phone_request_menu = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="📱 Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True
)

# ==================== ADMIN UCHUN KLAVIATURALAR ====================

def admin_menu():
    """Admin paneli menyusi."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 Foydalanuvchilar statistikasi")],
            [KeyboardButton(text="📢 Barchaga xabar yuborish"), KeyboardButton(text="👤 ID orqali xabar")],
            [KeyboardButton(text="⬅️ Asosiy menyu")]
        ],
        resize_keyboard=True
    ) 