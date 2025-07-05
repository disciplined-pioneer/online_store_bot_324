import asyncio
import logging
from services_runner.utils.payment_manager import PaymentManager


async def main():
    await asyncio.gather(
        asyncio.Task(PaymentManager().run(), name="payment_manager")
    )


if __name__ == "__main__":
    
    try:
        logging.info("✅ Бот запущен!")
        asyncio.run(main())

    except KeyboardInterrupt:
        logging.error("🛑 Бот остановлен вручную!")

    except Exception as e:
        logging.error(f"❌ Возникла критическая ошибка: {type(e).__name__}: {e}")
