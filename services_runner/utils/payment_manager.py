import os
import zipfile
import asyncio
import shutil
from pathlib import Path

from bot.core.bot import bot
from bot.settings import settings
from bot.core.logger import payment_manager_logger as logger

from aiogram.types import FSInputFile
from bot.templates.manager.payment_manager import *
from bot.keyboards.manager.payment_manager import *

from bot.db.models.enum import BillStatus
from bot.db.models.models import OrderUsers, Bill

from .encryption import Encryption
from bot.integrations.yookassa.yookassa_payment import YookassaPayment
from aiogram.exceptions import TelegramBadRequest


async def send_or_update_order_message(order: OrderUsers, bot, group_chat_id: int=settings.bot.CHANEL_ID):

    ZIP_DIR = "bot/data/zip"
    try:
        # Удаляем предыдущее сообщение, если есть
        if order.last_id_message_group:
            try:
                await bot.delete_message(chat_id=group_chat_id, message_id=order.last_id_message_group)
            except TelegramBadRequest:
                pass

        # Формируем текст и клавиатуру
        text = format_order_text(
            order_id=order.id,
            product_name=order.name,
            quantity=order.copies_count,
            total_price=order.price,
            address=order.geolocation,
            delivery_method=order.pickup,
            image_size=order.image_size,
            phone_number=order.phone_number,
        )
        reply_markup = await manager_panel_keyb(user_id=order.tg_id, order_id=order.id, bot=bot)

        # Список file_id
        file_ids = list(filter(None, order.file_id.split("/")))

        if len(file_ids) > 1:
            tg_id = str(order.tg_id)
            user_dir = os.path.join(ZIP_DIR, tg_id)
            os.makedirs(user_dir, exist_ok=True)

            file_paths = []
            for file_id in file_ids:
                tg_file = await bot.get_file(file_id)
                original_filename = os.path.basename(tg_file.file_path)
                local_path = os.path.join(user_dir, original_filename)
                await bot.download_file(tg_file.file_path, destination=local_path)
                file_paths.append(local_path)

            zip_path = os.path.join(ZIP_DIR, f"{tg_id}.zip")
            with zipfile.ZipFile(zip_path, "w") as zipf:
                for path in file_paths:
                    zipf.write(path, arcname=os.path.basename(path))

            sent_message = await bot.send_document(
                chat_id=group_chat_id,
                document=FSInputFile(zip_path),
                caption=text,
                reply_markup=reply_markup
            )

            # Удаляем все временные файлы и архив
            shutil.rmtree(user_dir, ignore_errors=True)
            if os.path.exists(zip_path):
                os.remove(zip_path)

        else:
            # Один файл — отправляем напрямую
            sent_message = await bot.send_document(
                chat_id=group_chat_id,
                document=file_ids[0],
                caption=text,
                reply_markup=reply_markup
            )

        await order.update(last_id_message_group=sent_message.message_id)
        return sent_message.message_id

    except Exception as e:
        logger.exception(f"Ошибка при отправке сообщения заказа #{order.id}: {e}")
        print(f'ошибка: {e}')
        
    except Exception as e:
        logger.exception(f"Ошибка при отправке сообщения заказа #{order.id}: {e}")
        print(f'ошибка: {e}')

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

        logger.info('===== Запуск задачи для проверки статуса платежей =====')
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
                    phone =metadata.get("phone")

                    address = ", ".join(filter(None, [
                        metadata.get("geolocation_city", ""),
                        metadata.get("geolocation_street", ""),
                        metadata.get("geolocation_house", "")
                    ]))

                    amount = float(data.get("amount", {}).get("value", 0.0))

                    # Проверка существующего заказа
                    existing_order = await OrderUsers.get_first(tg_id=bill.tg_id, dispatch_status='not_sent')

                    if existing_order:
                        
                        updated_price = existing_order.price + amount # Суммируем цену

                        def merge_always_slash(old: str, new: str, sep: str = "/") -> str:
                            return f"{old}{sep}{new}"

                        new_existing_order = await existing_order.update(
                            price=updated_price,
                            image_size=merge_always_slash(existing_order.image_size, metadata.get("image_size")),
                            copies_count=merge_always_slash(existing_order.copies_count, metadata.get("copies_count")),
                            phone_number=phone or existing_order.phone_number,
                            geolocation=merge_always_slash(existing_order.geolocation, address),
                            file_id=merge_always_slash(existing_order.file_id, metadata.get("file_id")),
                            file_type=merge_always_slash(existing_order.file_type, metadata.get("file_type")),
                            pickup=merge_always_slash(existing_order.pickup, metadata.get("pickup"))
                        )
                    else:
                        new_existing_order = await OrderUsers.create(
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

                    order_id = new_existing_order.id
                    await send_or_update_order_message(order=new_existing_order, bot=bot)
                    await bot.send_message(
                        chat_id=bill.tg_id,
                        text=f'✅ Оплата была получена для заказа №{order_id:06d}, спасибо за покупку! В ближайшее время менеджер оформит ваш заказ'
                    )
                    logger.info(f'Оплата пользователя {bill.tg_id} была подтверждена для заказа №{order_id:06d}')

            except Exception as e:
                logger.exception(f"Ошибка при проверке статуса счета {bill.bill_id}: {e}")
