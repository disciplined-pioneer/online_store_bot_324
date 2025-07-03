from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

size_selection_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="A5", callback_data="size:A5")],
        [InlineKeyboardButton(text="A4", callback_data="size:A4")],
        [InlineKeyboardButton(text="A3", callback_data="size:A3")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)


def previous_stepn_keyboard(parameter: str):
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"{parameter}")],
        ]
    )
    return keyb


delivery_pickup_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="ПВЗ Яндекс Маркет", callback_data="pickup_yandex")],
        [InlineKeyboardButton(text="ПВЗ OZON", callback_data="pickup_ozon")],
        [InlineKeyboardButton(text="Назад", callback_data="return_copies")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)
