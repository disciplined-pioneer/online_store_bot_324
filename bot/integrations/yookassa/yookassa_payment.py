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

    async def create(self, user_id: str, amount: float, data: dict, payment_method_id: str | None = None) -> dict:
        """
        Создаёт платёж в YooKassa с деталями заказа.
        :param user_id: ID пользователя
        :param amount: Общая сумма платежа (all_price)
        :param data: Словарь с деталями заказа
        :param payment_method_id: ID сохранённого метода оплаты
        :return: Ответ от YooKassa
        """

        # Описание позиции
        product_description = f"Печать: размер {data.get('image_size')}, копий: {data.get('copies_count')}"

        # Товары в чеке
        items = [{
            "description": product_description,
            "quantity": 1,
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "vat_code": 4,  # Без НДС
            "payment_mode": "full_payment",
            "payment_subject": "service"
        }]

        # Клиентские данные
        customer = {}
        if phone := data.get("phone_number"):
            customer["phone"] = phone

        # Плоская metadata
        geo = data.get("geolocation", {})
        file_info = data.get("file_info", {})

        metadata = {
            "price_per_copy": str(data.get("price", "")),
            "copies_count": str(data.get("copies_count", "")),
            "image_size": data.get("image_size", ""),
            "pickup": data.get("pickup", ""),
            "geolocation_city": geo.get("city", ""),
            "geolocation_street": geo.get("street", ""),
            "geolocation_house": geo.get("house", ""),
            "file_id": file_info.get("file_id", ""),
            "file_type": file_info.get("type", "")
        }

        # Сборка основного тела запроса
        json_body = {
            "amount": {"value": str(amount), "currency": "RUB"},
            "capture": True,
            "description": "Печать фото и документов",
            "metadata": metadata,
            "merchant_customer_id": str(user_id)
        }

        # Если это первый платёж
        if not payment_method_id:
            json_body.update({
                "save_payment_method": True,
                "test": True,
                "confirmation": {
                    "type": "redirect",
                    "return_url": f"https://t.me/{(await bot.get_me()).username}"
                },
                "receipt": {
                    "items": items,
                    "customer": customer
                }
            })
        else:
            json_body["payment_method_id"] = payment_method_id

        print(f"[DEBUG] Запрос в YooKassa: {json_body}")

        # Отправка запроса
        async with aiohttp.ClientSession('https://api.yookassa.ru') as session:
            response = await session.post(
                auth=self._auth,
                url="/v3/payments",
                headers={
                    "accept": "application/json",
                    "Idempotence-Key": str(uuid.uuid4())
                },
                json=json_body
            )

            response_text = await response.text()
            print(f"[DEBUG] Ответ от YooKassa: {response_text}")
            data = await response.json()

        # Проверка статуса запроса
        if response.status != 200:
            logger.error("Ошибка при создании платежа в YooKassa: %s", data)
            return {}

        logger.info("Платёж успешно создан: %s", data)
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