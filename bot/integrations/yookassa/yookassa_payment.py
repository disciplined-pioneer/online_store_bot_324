import uuid
from typing import Optional

import aiohttp

from ...core.bot import bot
from ...settings import settings
from ...core.logger import yookassa_logger as logger
from ...db.models.enum import BillStatus


class YookassaPayment:
    
    # Авторизация для доступа к API ЮKassa
    _auth = aiohttp.BasicAuth(
        login=str(settings.yookassa.SHOP_ID),
        password=settings.yookassa.TOKEN
    )

    async def create(self, user_id, amount: float, payment_method_id: str | None = None) -> dict:
        """
        Создаёт платёж в ЮKassa
        :param user_id: ID пользователя
        :param amount: Сумма платежа
        :param payment_method_id: ID сохранённого метода оплаты (если есть)
        :return: Данные платежа от ЮKassa
        """
        async with aiohttp.ClientSession('https://api.yookassa.ru') as s:
            # Если указан метод оплаты (ребил)1
            if payment_method_id:
                json = {
                    "amount": {"value": str(amount), "currency": "RUB"},
                    "capture": True,
                    "payment_method_id": payment_method_id,
                    "description": "Интернет магазин",
                    "merchant_customer_id": user_id,
                }
            else:
                # Первый платёж, с подтверждением через redirect
                json = {
                    "amount": {"value": str(amount), "currency": "RUB"},
                    "save_payment_method": True,
                    "merchant_customer_id": user_id,
                    "test": True,
                    "capture": True,
                    "description": "Интернет магазин",
                    "confirmation": {
                        "type": "redirect",
                        "return_url": f"https://t.me/{(await bot.get_me()).username}"
                    },
                    "receipt": {
                        "items": [
                            {
                                "payment_mode": "full_payment",
                                "payment_subject": "service",
                                "description": "Интернет магазин",
                                "quantity": 1,
                                "amount": {"value": str(amount), "currency": "RUB"},
                                "vat_code": 1,
                            }
                        ],
                        "customer": {
                            "email": "mmlomonosov@gmail.com",  # можно передавать email пользователя
                        }
                    },
                }

            print(f"[DEBUG] Запрос в ЮKassa: {json}")
            r = await s.post(
                auth=self._auth,
                url="/v3/payments",
                headers={
                    "accept": "application/json",
                    "Idempotence-Key": str(uuid.uuid4())
                },
                json=json
            )

            print(f"[DEBUG] Ответ от ЮKassa: {await r.text()}")
            data = await r.json()

        # Логирование ошибки, если запрос неуспешен
        if r.status != 200:
            logger.error("Ошибка при создании счёта в ЮKassa: %s", data)
            return {}

        # Успешное создание счёта
        logger.info("Счёт успешно создан в ЮKassa: %s", data)
        return data

    async def status(self, bill_id: str) -> tuple[Optional[BillStatus], dict]:
        """
        Проверка статуса платежа
        :param bill_id: ID платежа в ЮKassa
        :return: Статус платежа и данные
        """
        async with aiohttp.ClientSession('https://api.yookassa.ru') as session:
            response = await session.get(
                auth=self._auth,
                url=f"/v3/payments/{bill_id}",
                headers={
                    "accept": "application/json",
                    "Idempotence-Key": str(uuid.uuid4())
                },
            )

            print(f"[DEBUG] Ответ на запрос статуса: {await response.text()}")
            data = await response.json()

        # Лог ошибки, если статус не 200
        if response.status != 200:
            logger.error("Ошибка при получении статуса счёта в ЮKassa: %s", data)
            return None, data

        # Преобразование ответа в enum статус
        if data["status"] == "succeeded":
            return BillStatus.SUCCESS, data
        if data["status"] == "pending":
            return BillStatus.PENDING, data
        if data["status"] == "canceled":
            return BillStatus.FAIL, data

        # Неизвестный статус
        return BillStatus.UNKNOWN, data

    async def confirm_bill(self, bill_id: str) -> tuple[Optional[BillStatus], dict]:
        """
        Подтверждение оплаты по счёту (повтор запроса статуса)
        :param bill_id: ID платежа в ЮKassa
        :return: Статус платежа и данные
        """
        async with aiohttp.ClientSession('https://api.yookassa.ru') as session:
            response = await session.get(
                auth=self._auth,
                url=f"/v3/payments/{bill_id}",
                headers={
                    "accept": "application/json",
                    "Idempotence-Key": str(uuid.uuid4())
                },
            )

            print(f"[DEBUG] Подтверждение счёта: {await response.text()}")
            data = await response.json()

        if response.status != 200:
            logger.error("Ошибка при подтверждении счёта в ЮKassa: %s", data)
            return None, data

        if data["status"] == "succeeded":
            return BillStatus.SUCCESS, data
        if data["status"] == "pending":
            return BillStatus.PENDING, data
        if data["status"] == "canceled":
            return BillStatus.FAIL, data

        return BillStatus.UNKNOWN, data