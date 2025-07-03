from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

size_selection_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="A5", callback_data="size:A5")],
        [InlineKeyboardButton(text="A4", callback_data="size:A4")],
        [InlineKeyboardButton(text="A3", callback_data="size:A3")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

def get_order_confirmation_keyboard(number_order: int = 1):

    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"order_confirm:{number_order}")],
            [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
        ]
    )
    return keyb
