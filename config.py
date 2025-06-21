# -*- coding: utf-8 -*-

import os
from dotenv import load_dotenv

# .env faylidagi o'zgaruvchilarni yuklash
load_dotenv()

# -------------------- BOT SOZLAMALARI --------------------
# Bot tokeni muhit o'zgaruvchilaridan olinadi
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN muhit o'zgaruvchisi topilmadi!")

# -------------------- ADMIN SOZLAMALARI --------------------
# Admin ID si muhit o'zgaruvchilaridan olinadi
ADMIN_ID_STR = os.getenv("ADMIN_ID")
if not ADMIN_ID_STR or not ADMIN_ID_STR.isdigit():
    raise ValueError("ADMIN_ID muhit o'zgaruvchisi topilmadi yoki raqam emas!")
ADMIN_ID = int(ADMIN_ID_STR)

# -------------------- MA'LUMOTLAR BAZASI --------------------
# PostgreSQL ulanish manzili muhit o'zgaruvchilaridan olinadi
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL muhit o'zgaruvchisi topilmadi!")

# -------------------- KANALLAR SOZLAMALARI --------------------
# Majburiy obuna kanallari (vergul bilan ajratilgan holda)
CHANNELS_STR = os.getenv("CHANNELS", "@BlokTest_uz,@CyberDataFort")
CHANNELS = [channel.strip() for channel in CHANNELS_STR.split(',')]

# Ro'yxatdan o'tish kanali
REG_CHANNEL_STR = os.getenv("REG_CHANNEL")
REG_CHANNEL = int(REG_CHANNEL_STR) if REG_CHANNEL_STR and REG_CHANNEL_STR.lstrip('-').isdigit() else REG_CHANNEL_STR

# -------------------- WEBAPP SOZLAMALARI --------------------
WEBAPP_URL_TELEGRAM = os.getenv("WEBAPP_URL_TELEGRAM", 'https://blok-tets.uz/')
WEBAPP_URL_SITE = os.getenv("WEBAPP_URL_SITE", 'https://t.me/BlokTest_uz/6')

# -------------------- QO'SHIMCHA SOZLAMALAR --------------------
SUPPORT_GROUP_URL = os.getenv("SUPPORT_GROUP_URL", 'https://t.me/BlokTestuz_support')
PARTNERSHIP_FORM_FIELDS = [
    "O'quv markaz nomi",
    "Manzil",
    "Telefon raqam",
    "Hamkorlik turi",
    "Qo'shimcha ma'lumotlar (barchasini bir xabarda yuboring!)"
]

# Ma'lumotlar bazasi fayli nomi
DB_NAME = 'database.db' 