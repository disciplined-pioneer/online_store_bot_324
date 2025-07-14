import logging
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...db.models.models import Users
from ...utils.user.commands import process_start_payload
from ...services.user.commands import save_or_update_user
from ...templates.user.commands import hello_user_msg
from ...keyboards.user.commands import start_user_keyb
from ...utils.user.examples import get_media_by_index

from ...templates.admin.commands import hello_admin_msg
from ...keyboards.admin.commands import start_admin_keyb


router = Router()


# Старт
@router.message(Command("start", ignore_case=True))
async def cmd_start(message: Message, state: FSMContext):

    # Удаление истории сообщений
    await message.delete()
    data = await state.get_data()
    report_id = data.get("report", message.message_id - 90)

    try:
        await bot.delete_messages(
            chat_id=message.chat.id,
            message_ids=list(range(
                max(1, message.message_id - 90, report_id + 1),
                message.message_id + 1
            ))
        )
    except Exception:
        pass

    # Сохранение или обновление пользователя
    tg_id = message.from_user.id
    name = message.from_user.full_name

    # Обработка реферальной ссылки
    referral_code = await process_start_payload(tg_id=tg_id, message=message)
    await save_or_update_user(tg_id=tg_id, name=name, referral_code=referral_code)

    # Получение информации о пользователе
    info_user = await Users.get(tg_id=tg_id)
    role = info_user.role

    # Поведение для админа
    if role == "admin":
        new_msg = await message.answer(
            text=hello_admin_msg,
            reply_markup=start_admin_keyb
        )

    # Поведение для пользователя
    else:
        text = hello_user_msg
        keyboard = await start_user_keyb(bot)

        media, _ = get_media_by_index("additional_images", 1)

        if media:
            try:
                new_msg = await media.send(
                    msg=message,
                    caption=text,
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке медиа пользователю: {e}")
                new_msg = await message.answer(text=text, reply_markup=keyboard)
        else:
            new_msg = await message.answer(text=text, reply_markup=keyboard)

    # Обновляем state
    await state.update_data(last_id_message=new_msg.message_id)
