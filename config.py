# -*- coding: utf-8 -*-
import os
from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni o'qish (agar mavjud bo'lsa)
load_dotenv()

# -------------------- BOT SOZLAMALARI --------------------
# Bot tokeni Render'dagi Environment Variables'dan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN")

# -------------------- ADMIN SOZLAMALARI --------------------
# Admin ID raqami Render'dagi Environment Variables'dan olinadi
ADMIN_ID = int(os.getenv("ADMIN_ID", 0))

# -------------------- MA'LUMOTLAR BAZASI --------------------
# PostgreSQL manzili Render tomonidan avtomatik ta'minlanadi
DATABASE_URL = os.getenv("DATABASE_URL")

# -------------------- KANALLAR --------------------
# Kanallar ro'yxati (vergul bilan ajratilgan holda, masalan: @kanal1,@kanal2)
CHANNELS_STR = os.getenv("CHANNELS", "")
CHANNELS = [channel.strip() for channel in CHANNELS_STR.split(',') if channel.strip()]

# -------------------- RO'YXATDAN O'TISH KANALI --------------------
REG_CHANNEL = os.getenv("REG_CHANNEL")

# -------------------- QO'LLAB-QUVVATLASH GURUHI --------------------
SUPPORT_GROUP_URL = os.getenv("SUPPORT_GROUP_URL", "https://t.me/my_support_group")

# -------------------- WEBAPP SOZLAMALARI --------------------
WEBAPP_URL_TELEGRAM = os.getenv("WEBAPP_URL_TELEGRAM", "https://t.me/my_bot/my_app")
WEBAPP_URL_SITE = os.getenv("WEBAPP_URL_SITE", "https://my-site.com")

# -------------------- HAMKORLIK UCHUN SO'ROVNOMA --------------------
PARTNERSHIP_FORM_FIELDS = [
    "Tashkilot nomi",
    "Mas'ul shaxs",
    "Telefon raqam",
    "Hamkorlik taklifi"
] 