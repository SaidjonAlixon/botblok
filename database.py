import asyncpg
import logging
from config import DATABASE_URL

# Logging sozlamalari
logging.basicConfig(level=logging.INFO)

# Global connection pool
pool = None

async def init_db():
    """Ma'lumotlar bazasi bilan aloqa (connection pool) yaratadi va jadval mavjudligini tekshiradi."""
    global pool
    if pool is None:
        try:
            pool = await asyncpg.create_pool(DATABASE_URL)
            logging.info("PostgreSQL bilan aloqa o'rnatildi va connection pool yaratildi.")
        except Exception as e:
            logging.critical(f"PostgreSQL ga ulanishda jiddiy xatolik: {e}")
            return

    async with pool.acquire() as connection:
        await connection.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                user_id BIGINT UNIQUE NOT NULL,
                fullname TEXT NOT NULL,
                age TEXT,
                region TEXT,
                phone TEXT,
                username TEXT,
                registration_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    logging.info("'users' jadvali muvaffaqiyatli ishga tushirildi.")

async def add_user(user_id, fullname, age, region, phone, username):
    """Foydalanuvchini bazaga qo'shadi va uning tartib raqamini qaytaradi."""
    query = """
        INSERT INTO users (user_id, fullname, age, region, phone, username) 
        VALUES ($1, $2, $3, $4, $5, $6)
        ON CONFLICT (user_id) DO NOTHING
        RETURNING id;
    """
    async with pool.acquire() as connection:
        user_number = await connection.fetchval(query, user_id, fullname, age, region, phone, username or '')
        if user_number:
            logging.info(f"Yangi foydalanuvchi {user_id} ({fullname}) bazaga qo'shildi. Tartib raqami: {user_number}")
        return user_number

async def user_exists(user_id):
    """Foydalanuvchi bazada mavjudligini tekshiradi."""
    query = "SELECT EXISTS(SELECT 1 FROM users WHERE user_id = $1)"
    async with pool.acquire() as connection:
        return await connection.fetchval(query, user_id)

async def get_user(user_id):
    """Foydalanuvchi ma'lumotlarini ID orqali oladi va lug'at (dict) ko'rinishida qaytaradi."""
    query = "SELECT * FROM users WHERE user_id = $1"
    async with pool.acquire() as connection:
        row = await connection.fetchrow(query, user_id)
        return dict(row) if row else None

async def get_users_count():
    """Barcha foydalanuvchilar sonini qaytaradi."""
    query = "SELECT COUNT(*) FROM users"
    async with pool.acquire() as connection:
        return await connection.fetchval(query)

async def get_all_user_ids():
    """Barcha foydalanuvchilarning ID larini ro'yxat qilib qaytaradi."""
    query = "SELECT user_id FROM users"
    async with pool.acquire() as connection:
        rows = await connection.fetch(query)
        return [row['user_id'] for row in rows] 