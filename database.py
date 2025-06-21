# -*- coding: utf-8 -*-

import asyncpg
import logging
from config import DATABASE_URL

# Global connection pool
pool: asyncpg.Pool = None

async def create_pool():
    """PostgreSQL uchun connection pool yaratadi."""
    global pool
    try:
        pool = await asyncpg.create_pool(dsn=DATABASE_URL)
        logging.info("PostgreSQL connection pool muvaffaqiyatli yaratildi.")
    except Exception as e:
        logging.critical(f"Connection pool yaratishda xatolik: {e}")
        raise

async def init_db():
    """Ma'lumotlar bazasini ishga tushiradi va kerakli jadvallarni yaratadi."""
    async with pool.acquire() as conn:
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                username TEXT,
                full_name TEXT,
                age TEXT,
                region TEXT,
                phone TEXT,
                join_date TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        logging.info("'users' jadvali mavjud yoki muvaffaqiyatli yaratildi.")

async def add_user(user_id: int, username: str, full_name: str, age: str, region: str, phone: str):
    """Foydalanuvchini bazaga qo'shadi. Agar foydalanuvchi yangi bo'lsa True qaytaradi."""
    sql = """
        INSERT INTO users (user_id, username, full_name, age, region, phone)
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id) DO NOTHING
    """
    async with pool.acquire() as conn:
        result = await conn.execute(sql, user_id, username, full_name, age, region, phone)
        return "INSERT 0 1" in result

async def user_exists(user_id: int) -> bool:
    """Foydalanuvchi bazada mavjudligini tekshiradi."""
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT 1 FROM users WHERE user_id = $1", user_id) is not None

async def count_users() -> int:
    """Barcha foydalanuvchilar sonini qaytaradi."""
    async with pool.acquire() as conn:
        return await conn.fetchval("SELECT COUNT(*) FROM users")

async def get_all_user_ids() -> list:
    """Barcha foydalanuvchilarning ID'larini ro'yxat qilib qaytaradi."""
    async with pool.acquire() as conn:
        rows = await conn.fetch("SELECT user_id FROM users")
        return [row['user_id'] for row in rows]

async def get_user(user_id: int) -> dict:
    """Foydalanuvchi ma'lumotlarini lug'at (dict) ko'rinishida qaytaradi."""
    async with pool.acquire() as conn:
        row = await conn.fetchrow("SELECT * FROM users WHERE user_id = $1", user_id)
        return dict(row) if row else None 