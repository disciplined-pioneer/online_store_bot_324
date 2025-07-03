from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

size_selection_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="A5", callback_data="size:A5")],
        [InlineKeyboardButton(text="A4", callback_data="size:A4")],
        [InlineKeyboardButton(text="A3", callback_data="size:A3")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)
