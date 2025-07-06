import asyncio
from pathlib import Path

from bot.core.bot import bot
from bot.settings import settings
from bot.core.logger import payment_manager_logger as logger

from bot.templates.manager.payment_manager import *
from bot.keyboards.manager.payment_manager import *

from bot.db.models.enum import BillStatus
from bot.db.models.models import OrderUsers, Bill

from .encryption import Encryption
from bot.integrations.yookassa.yookassa_payment import YookassaPayment

from aiogram.types import InputMediaPhoto, Message
from aiogram.exceptions import TelegramBadRequest


async def send_or_update_order_message(order: OrderUsers, group_chat_id: int, bot):
    try:
        # 1. Удаляем старое сообщение, если было
        if order.last_id_message_group:
            try:
                await bot.delete_message(chat_id=group_chat_id, message_id=order.last_id_message_group)
            except TelegramBadRequest:
                pass  # сообщение не найдено или уже удалено

        # 2. Собираем caption (текст)
        text = format_order_text(
            order_id=order.id,
            product_name=order.name,
            quantity=sum(map(int, order.copies_count.split("/"))),  # объединённые копии
            total_price=order.price,
            address=order.geolocation,
            delivery_method=order.pickup,
            image_size=order.image_size,
            phone_number=order.phone_number,
        )

        # 3. Собираем клавиатуру
        reply_markup = await manager_panel_keyb(user_id=order.tg_id, order_id=order.id, bot=bot)

        # 4. Обработка изображений
        file_ids = list(set(filter(None, order.file_id.split("/"))))
        if len(file_ids) > 1:
            # Группа изображений
            media = [
                InputMediaPhoto(media=file_id, caption=text if i == 0 else None)
                for i, file_id in enumerate(file_ids)
            ]
            messages: list[Message] = await bot.send_media_group(chat_id=group_chat_id, media=media)
            sent_message = messages[0]  # caption только в первом сообщении
            await bot.edit_message_reply_markup(chat_id=group_chat_id, message_id=sent_message.message_id, reply_markup=reply_markup)
        else:
            # Одно изображение
            sent_message = await bot.send_photo(
                chat_id=group_chat_id,
                photo=file_ids[0],
                caption=text,
                reply_markup=reply_markup
            )

        # 5. Обновляем id последнего сообщения
        await order.update(last_id_message_group=sent_message.message_id)

    except Exception as e:
        logger.exception(f"Ошибка при отправке сообщения заказа #{order.id}: {e}")


class PaymentManager():

    timeout = 10
    yookassa = YookassaPayment()
    enc = Encryption(Path("secret/key.pem"))

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
                decrypted_bill_id = self.enc.decrypt(bill.bill_id.encode())
                status, data = await self.yookassa.status(decrypted_bill_id)

                if status in (BillStatus.PENDING, BillStatus.UNKNOWN): # Если не обработан
                    continue

                if status == BillStatus.FAIL: # Отменён или отклонён
                    await bill.update(status=status)
                    continue

                if status == BillStatus.SUCCESS: # Прошёл успешно

                    await bill.update(status=status)

                    # Распаковка данных
                    metadata = data.get("metadata", {})
                    phone = data.get("receipt", {}).get("customer", {}).get("phone") or metadata.get("phone_number")

                    address = ", ".join(filter(None, [
                        metadata.get("geolocation_city", ""),
                        metadata.get("geolocation_street", ""),
                        metadata.get("geolocation_house", "")
                    ]))

                    amount = float(data.get("amount", {}).get("value", 0.0))

                    # Проверка существующего заказа
                    existing_order = await OrderUsers.filter(tg_id=bill.tg_id, dispatch_status='not_sent')

                    if existing_order:
                        
                        updated_price = existing_order.price + amount # Суммируем цену

                        def merge_unique(old: str, new: str, sep: str = "/") -> str:
                            items = set(filter(None, (old or "").split(sep) + (new or "").split(sep)))
                            return sep.join(sorted(items))

                        await existing_order.update(
                            price=updated_price,
                            image_size=merge_unique(existing_order.image_size, metadata.get("image_size")),
                            copies_count=merge_unique(existing_order.copies_count, metadata.get("copies_count")),
                            phone_number=phone or existing_order.phone_number,
                            geolocation=merge_unique(existing_order.geolocation, address, sep=", "),
                            file_id=merge_unique(existing_order.file_id, metadata.get("file_id")),
                            file_type=merge_unique(existing_order.file_type, metadata.get("file_type")),
                            pickup=merge_unique(existing_order.pickup, metadata.get("pickup"))
                        )
                    else:
                        await OrderUsers.create(
                            tg_id=bill.tg_id,
                            name='Картины на металле',
                            price=amount,
                            image_size=metadata.get('image_size'),
                            copies_count=metadata.get('copies_count'),
                            phone_number=phone,
                            geolocation=address,
                            file_id=metadata.get('file_id'),
                            file_type=metadata.get('file_type'),
                            pickup=metadata.get('pickup')
                        )

                    await send_or_update_order_message(order=existing_order, group_chat_id=settings.bot.CHANEL_ID, bot=bot)

            except Exception as e:
                logger.exception(f"Ошибка при проверке статуса счета {bill.bill_id}: {e}")
