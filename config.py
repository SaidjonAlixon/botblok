# -*- coding: utf-8 -*-

# -------------------- BOT SOZLAMALARI --------------------
# Quyidagi qatorga o'z botingizning tokenini yozing
# Misol: BOT_TOKEN = "1234567890:ABCdEFG..."
BOT_TOKEN = "7436749862:AAFmCV4bVCaYUJirNL2_6uAa1H7ubF_zGRM" 

if BOT_TOKEN == "PASTE_YOUR_BOT_TOKEN_HERE":
    raise ValueError("Iltimos, config.py faylida o'z botingizning tokenini kiriting!")

# -------------------- ADMIN SOZLAMALARI --------------------
# Bu yerga o'zingizning Telegram ID raqamingizni yozing
# Misol: ADMIN_ID = 123456789
ADMIN_ID = 5222899144  # O'zingizning ID raqamingizni kiriting

if ADMIN_ID == 5222899144:
    print("DIQQAT: config.py faylida o'z ADMIN_ID raqamingizni kiritmagansiz!")


# -------------------- MA'LUMOTLAR BAZASI --------------------
# Ma'lumotlar bazasi fayli nomi
DB_NAME = 'database.db'
DATABASE_URL = f"sqlite+aiosqlite:///{DB_NAME}"


# -------------------- KANALLAR SOZLAMALARI --------------------
# Majburiy obuna kanallari (foydalanuvchi nomi bilan, @ belgisini qo'shing)
CHANNELS = ["@BlokTest_uz", "@CyberDataFort"]

# Ro'yxatdan o'tgan foydalanuvchilar haqida xabar yuboriladigan kanal IDsi
# Kanal ID raqam bo'lishi kerak, minus (-) belgisi bilan boshlanishi mumkin
# Misol: REG_CHANNEL = -100123456789
REG_CHANNEL = -1002706857485 # O'zingizning kanalingiz ID sini kiriting

# -------------------- WEBAPP SOZLAMALARI --------------------
WEBAPP_URL_TELEGRAM = 'https://blok-tets.uz/'
WEBAPP_URL_SITE = 'https://t.me/BlokTest_uz/6'

# -------------------- QO'SHIMCHA SOZLAMALAR --------------------
SUPPORT_GROUP_URL = 'https://t.me/BlokTestuz_support'
PARTNERSHIP_FORM_FIELDS = [
    "O'quv markaz nomi",
    "Manzil",
    "Telefon raqam",
    "Hamkorlik turi",
    "Qo'shimcha ma'lumotlar (barchasini bir xabarda yuboring!)"
] 