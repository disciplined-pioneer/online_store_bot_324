import asyncio
import logging
from aiogram import Dispatcher
from aiogram.types import BotCommandScopeDefault

from core.bot import bot
from settings import settings
from bot.handlers import routers

from db.crud.base import init_postgres
from services.user.commands import add_admins, create_data_folders

dp = Dispatcher()

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

dp.include_routers(*routers)

async def main():
    
    await init_postgres()

    await add_admins() # Добавление админов
    create_data_folders()
        
    await bot.set_my_commands(
        commands=settings.bot.COMMANDS,
        scope=BotCommandScopeDefault()
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    
    try:
        logging.info("✅ Бот запущен!")
        asyncio.run(main())

    except KeyboardInterrupt:
        logging.error("🛑 Бот остановлен вручную!")

    except Exception as e:
        logging.error(f"❌ Возникла критическая ошибка: {type(e).__name__}: {e}")