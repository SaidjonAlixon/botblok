# -*- coding: utf-8 -*-

# -------------------- BOT SOZLAMALARI --------------------
# Quyidagi qatorga o'z botingizning tokenini yozing
# Misol: BOT_TOKEN = "1234567890:ABCDEFG..."
BOT_TOKEN = "PASTE_YOUR_BOT_TOKEN_HERE"

# -------------------- ADMIN SOZLAMALARI --------------------
# Bu yerga o'zingizning Telegram ID raqamingizni yozing
# Misol: ADMIN_ID = 123456789
ADMIN_ID = 0 # O'zingizning ID raqamingizni kiriting

# -------------------- MA'LUMOTLAR BAZASI --------------------
# PostgreSQL uchun ulanish manzili. Render kabi xostinglarda avtomatik sozlanadi.
# Misol: DATABASE_URL="postgresql://user:password@host:port/database"
DATABASE_URL = "postgresql://user:password@host:port/database"

# -------------------- KANALLAR --------------------
# Botdan foydalanish uchun majburiy obuna bo'lish kerak bo'lgan kanallar
# Misol: CHANNELS = ["@test_kanal", "@ikkinchi_kanal"]
CHANNELS = []

# -------------------- RO'YXATDAN O'TISH KANALI --------------------
# Yangi foydalanuvchilar haqida ma'lumot yuboriladigan kanal
# Kanal ID'sini (masalan, -100123456789) yoki username'ini (masalan, "@my_reg_channel") kiriting
REG_CHANNEL = None

# -------------------- QO'LLAB-QUVVATLASH GURUHI --------------------
SUPPORT_GROUP_URL = "https://t.me/my_support_group"

# -------------------- WEBAPP SOZLAMALARI --------------------
WEBAPP_URL_TELEGRAM = "https://t.me/my_bot/my_app" # Telegram WebApp uchun to'liq URL
WEBAPP_URL_SITE = "https://my-site.com" # Tashqi sayt uchun URL

# -------------------- HAMKORLIK UCHUN SO'ROVNOMA --------------------
PARTNERSHIP_FORM_FIELDS = [
    "Tashkilot nomi",
    "Mas'ul shaxs",
    "Telefon raqam",
    "Hamkorlik taklifi"
] 