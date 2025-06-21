# -*- coding: utf-8 -*-

import aiosqlite
from config import DB_NAME

# Ma'lumotlar bazasini yaratish va unga ulanish
async def init_db():
    """Ma'lumotlar bazasini yaratadi va unga kerakli jadvallarni qo'shadi."""
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                age TEXT,
                region TEXT,
                phone TEXT,
                join_date DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        await db.commit()

# Foydalanuvchi qo'shish
async def add_user(user_id: int, username: str, full_name: str, age: str, region: str, phone: str):
    """Foydalanuvchini bazaga qo'shadi va u mavjud bo'lmasa True qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        user_exists = await cursor.fetchone()
        
        if not user_exists:
            await db.execute(
                "INSERT INTO users (user_id, username, full_name, age, region, phone) VALUES (?, ?, ?, ?, ?, ?)",
                (user_id, username, full_name, age, region, phone)
            )
            await db.commit()
            return True
        return False

async def user_exists(user_id: int):
    """Foydalanuvchi bazada mavjudligini tekshiradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
        return await cursor.fetchone() is not None

# Barcha foydalanuvchilar sonini olish
async def count_users():
    """Barcha foydalanuvchilar sonini qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT COUNT(*) FROM users")
        count = await cursor.fetchone()
        return count[0] if count else 0

# Barcha foydalanuvchilar ID'larini olish
async def get_all_user_ids():
    """Barcha foydalanuvchilarning ID'larini ro'yxat qilib qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        cursor = await db.execute("SELECT user_id FROM users")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]

# Foydalanuvchi ma'lumotlarini olish
async def get_user(user_id: int):
    """Foydalanuvchi ma'lumotlarini lug'at (dict) ko'rinishida qaytaradi."""
    async with aiosqlite.connect(DB_NAME) as db:
        db.row_factory = aiosqlite.Row # Natijalarni dict ko'rinishida olish uchun
        cursor = await db.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user_data = await cursor.fetchone()
        return dict(user_data) if user_data else None 