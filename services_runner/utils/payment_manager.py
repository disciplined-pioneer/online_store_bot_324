import asyncio

from bot.core.bot import bot
from bot.core.logger import payment_manager_logger as logger
from .encryption import Encryption
from bot.integrations.yookassa.yookassa_payment import YookassaPayment


class PaymentManager():

    timeout = 10
    yookassa = YookassaPayment()
    enc = Encryption()

    async def run(self):
        logger.info('=== Менеджер платежей работает ===')
        while True:
            try:
                await self.task()

            except Exception as e:
                logger.error("Ошибка API при запуске платежного менеджера: %s", e)

            await asyncio.sleep(self.timeout)

    async def task(self):
        pass