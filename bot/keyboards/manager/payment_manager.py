from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def manager_panel_keyb(user_id: int, order_id: int, bot):
    
    base_buttons = [
        [InlineKeyboardButton(text="Отправить", callback_data=f"send:{user_id}:{order_id}")],
        [InlineKeyboardButton(text="Адрес", callback_data=f"address:{user_id}:{order_id}")]
    ]

    try:
        # Проверяем, существует ли пользователь
        await bot.get_chat(user_id)
        base_buttons.append([
            InlineKeyboardButton(text="Связаться", url=f"tg://user?id={user_id}")
        ])
    except TelegramBadRequest:
        base_buttons.append([
            InlineKeyboardButton(text="Связаться (недоступен)", callback_data='contact_unavailable')
        ])

    base_buttons.append([
        InlineKeyboardButton(text="Оповестить о сформированной доставке", callback_data=f"notify:{user_id}:{order_id}")
    ])

    return InlineKeyboardMarkup(inline_keyboard=base_buttons)

def back_manager_menu(user_id: int, order_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"back_manager:{user_id}:{order_id}")],
        ]
    )
