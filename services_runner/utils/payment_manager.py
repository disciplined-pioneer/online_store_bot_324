import asyncio


from bot.core.bot import bot
from bot.settings import settings
from bot.core.logger import payment_manager_logger as logger

from bot.templates.manager.payment_manager import *
from bot.keyboards.manager.payment_manager import *

from bot.db.models.enum import BillStatus
from bot.db.models.models import OrderUsers, Bill

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

        bills = await Bill.filter(status=BillStatus.PENDING)

        for bill in bills:
            try:
                status, data = await self.yookassa.status(bill.bill_id)

                if status in (BillStatus.PENDING, BillStatus.UNKNOWN):
                    continue  # ждем подтверждения дальше

                if status == BillStatus.FAIL:
                    await bill.update(status=status)
                    continue

                if status == BillStatus.SUCCESS:
                    await bill.update(status=status)

                    # Проверка на наличие уже существующих заказов в БД
                    """info_user_order = await OrderUsers.filter(tg_id=tg_id, dispatch_status='not_sent')
                    if info_user_order:
                        pass
                    else:"""

                    """await bot.send_photo(
                        chat_id=settings.bot.CHANEL_ID,
                        photo=file_id,
                        caption=format_order_text(),
                        reply_markup=await manager_panel_keyb(user_id=, order_id=, bot=bot)
                    )

                    await bot.send_document(
                        chat_id=settings.bot.CHANEL_ID,
                        photo=file_id,
                        caption=format_order_text(),
                        reply_markup=await manager_panel_keyb(user_id=, order_id=, bot=bot)
                    )"""


            except Exception as e:
                logger.exception(f"Ошибка при проверке статуса счета {bill.bill_id}: {e}")
