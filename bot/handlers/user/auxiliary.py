import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext

from ...db.models.models import Users
from aiogram.types import CallbackQuery

from ...core.bot import bot
from ...templates.user.commands import hello_user_msg
from ...keyboards.user.commands import start_user_keyb
from ...utils.user.commands import process_start_payload
from ...services.user.commands import save_or_update_user
from ...utils.user.examples import get_media_by_index

from ...templates.admin.commands import hello_admin_msg
from ...keyboards.admin.commands import start_admin_keyb


router = Router()


# Обработка кнопки "Меню" - когда в сообщении изображение
@router.callback_query(F.data == "back_menu")
@router.callback_query(F.data == "back_menu:images")
async def back_buttons_images(callback: types.CallbackQuery, state: FSMContext):

    # Удаление истории сообщений
    await callback.message.delete()
    data = await state.get_data()
    report_id = data.get("report", callback.message.message_id - 90)

    try:
        await bot.delete_messages(
            chat_id=callback.message.chat.id,
            message_ids=list(range(
                max(1, callback.message.message_id - 90, report_id + 1),
                callback.message.message_id + 1
            ))
        )
    except Exception:
        pass

    # Сохранение или обновление пользователя
    tg_id = callback.from_user.id
    name = callback.from_user.full_name
    await save_or_update_user(tg_id=tg_id, name=name)

    # Обработка реферальной ссылки
    await process_start_payload(tg_id=tg_id, message=callback.message)

    # Получение информации о пользователе
    info_user = await Users.get(tg_id=tg_id)
    role = info_user.role

    # Поведение для админа
    if role == "admin":
        new_msg = await callback.message.answer(
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
                    msg=callback.message,
                    caption=text,
                    reply_markup=keyboard
                )
            except Exception as e:
                logging.error(f"Ошибка при отправке медиа пользователю: {e}")
                new_msg = await callback.message.answer(text=text, reply_markup=keyboard)
        else:
            new_msg = await callback.message.answer(text=text, reply_markup=keyboard)

    # Обновляем state
    await state.update_data(last_id_message=new_msg.message_id)


# Когда поддержка недоступна
@router.callback_query(F.data == "support_unavailable")
async def support_unavailable_cb(query: CallbackQuery):
    await query.answer(
        "Поддержка временно недоступна ⏳",
        show_alert=True
    )


# Когда менеджер недоступен
@router.callback_query(F.data == "manager_unavailable")
async def support_unavailable_cb(query: CallbackQuery):
    await query.answer(
        "Менеджер временно недоступен ⏳",
        show_alert=True
    )


# Удаление сообщений, не подключённых к состоянию
@router.message()
async def handle_unexpected_message(message: types.Message, state: FSMContext):
    print('🛑 Удаляем сообщение - не в состоянии 🛑')
    await message.delete()    