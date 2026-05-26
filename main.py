import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from config import BOT_TOKEN
from database import db
from handlers import user, admin

# Logging setup
logging.basicConfig(level=logging.INFO)

async def main():
    # Initialize DB
    await db.init_db()
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Register Routers
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    # Start polling
    logging.info("Bot is starting...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Bot stopped!")
