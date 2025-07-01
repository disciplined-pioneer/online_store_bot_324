from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_admin_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пока ничего тут нет", callback_data='test')]
    ]
)
