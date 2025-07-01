from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

start_user_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Примеры работ", callback_data='examples')],
        [InlineKeyboardButton(text="Заказать", callback_data='order')],
        [InlineKeyboardButton(text="Мои заказы", callback_data='my_orders')],
        [InlineKeyboardButton(text="Отзывы", callback_data='reviews')],
        [InlineKeyboardButton(text="Поддержка", callback_data='support')]
    ]
)
