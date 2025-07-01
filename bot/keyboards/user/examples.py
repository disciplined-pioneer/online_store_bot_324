from settings import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

examples_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Картины на металле", callback_data="")],
        [InlineKeyboardButton(text="Индивидуальная гравировка", callback_data="")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)
