import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, ADMIN_ID, REG_CHANNEL
from database import init_db
from handlers.user import user_router
from handlers.admin import admin_router

# Logging sozlamalari
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
)

async def on_startup(bot: Bot):
    """Bot ishga tushganda bajariladigan amallar."""
    await init_db()
    logging.info("Ma'lumotlar bazasi muvaffaqiyatli ishga tushirildi.")
    
    # Ro'yxatdan o'tish kanalini tekshirish
    if REG_CHANNEL:
        try:
            chat = await bot.get_chat(REG_CHANNEL)
            logging.info(f"✅ Ro'yxatdan o'tish kanali '{chat.title}' ({REG_CHANNEL}) topildi va sozlamalar to'g'ri.")
        except Exception as e:
            logging.error(
                f"❌ DIQQAT! Ro'yxatdan o'tish kanalini ({REG_CHANNEL}) topishda xatolik!\n"
                f"Sabab: {e}\n"
                f"Iltimos, quyidagilarni tekshiring:\n"
                f"1. 'config.py' faylida REG_CHANNEL to'g'ri kiritilganmi?\n"
                f"2. Bot ushbu kanalga a'zo qilinganmi?\n"
                f"3. Bot ushbu kanalda xabar yuborish huquqi bilan admin qilinganmi?"
            )
    else:
        logging.warning("Ma'lumot yuboriladigan ro'yxatdan o'tish kanali (REG_CHANNEL) 'config.py' da ko'rsatilmagan.")
        
    # Adminga bot ishga tushgani haqida xabar yuborish
    try:
        await bot.send_message(ADMIN_ID, "✅ Bot muvaffaqiyatli ishga tushirildi!")
    except Exception as e:
        logging.error(f"Adminga ({ADMIN_ID}) xabar yuborishda xato: {e}. ADMIN_ID to'g'riligini tekshiring.")

async def on_shutdown(dp: Dispatcher):
    """Bot to'xtaganda connection pool ni yopadi."""
    from database import pool
    if pool:
        await pool.close()
        logging.info("PostgreSQL connection pool yopildi.")

async def main():
    """Botni ishga tushiradi."""
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)

    # Routerlarni ulash
    dp.include_router(admin_router)
    dp.include_router(user_router)
    
    # Bot ishga tushganda va to'xtaganda bajariladigan funksiyalarni ro'yxatdan o'tkazish
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # Botni ishga tushirish
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    except Exception as e:
        logging.critical(f"Botni ishga tushirishda jiddiy xatolik: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        logging.info("Bot ishga tushirilmoqda...")
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot to'xtatildi.") 