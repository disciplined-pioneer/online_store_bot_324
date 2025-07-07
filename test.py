import asyncio
from bot.db.crud.base import init_postgres
from bot.core.bot import bot
from bot.settings import settings
from bot.db.models.models import OrderUsers
from services_runner.utils.payment_manager import send_or_update_order_message

async def main():
    await init_postgres()
    amount = 1999.99

    # Псевдоданные, которые ты должен сам определить
    metadata = {
        "image_size": "30x40",
        "copies_count": "2",
        "file_id": "AgACAgIAAxkDAANVaGo8F4HA8odIwMA-6PcBRufYGacAAgr5MRv1IlFLZElxX8mF9VMBAAMCAAN5AAM2BA",
        "file_type": "photo",
        "pickup": "pickup",
    }
    phone = "+79998887766"
    address = "Москва, ул. Пушкина, д. 1"

    new_order = await OrderUsers.create(
        tg_id=802587774,
        name='@yluxw',
        price=amount,
        image_size=metadata["image_size"],
        copies_count=metadata["copies_count"],
        phone_number=phone,
        geolocation=address,
        file_id=metadata["file_id"],
        file_type=metadata["file_type"],
        pickup=metadata["pickup"],
        dispatch_status="not_sent",
        last_id_message_group=None
    )

    # Обновление/отправка сообщения (если нужно)
    print(settings.bot.CHANEL_ID)
    id_message_group = await send_or_update_order_message(
        order=new_order, 
        group_chat_id=settings.bot.CHANEL_ID,
        bot=bot
    )

    await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
