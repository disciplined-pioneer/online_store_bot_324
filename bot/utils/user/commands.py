import logging
from aiogram.types import Message
from ...db.models.models import ReferralLinks, Users

async def process_start_payload(message: Message, tg_id: int):
    """
    Извлекает payload из команды /start и, если он есть,
    обрабатывает его как ID реферальной ссылки.
    """
    if not message.text or await Users.get(tg_id=tg_id):
        return None

    parts = message.text.strip().split()
    if len(parts) != 2 or parts[0].lower() != "/start":
        return None

    payload = parts[1]

    try:
        # Явное приведение к int, чтобы соответствовать типу id в БД
        payload_id = int(payload)

        info_link = await ReferralLinks.get(id=payload_id)
        if info_link:
            await info_link.update(number_users=info_link.number_users + 1)
            return payload_id
        
    except ValueError:
        logging.error(f"[ERROR] payload не является числом: {payload}")
    except Exception as e:
        logging.error(f"[ERROR] Ошибка при обработке payload: {e}")
    
    return None
