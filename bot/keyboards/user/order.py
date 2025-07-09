from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

image_menu = InlineKeyboardMarkup(
    inline_keyboard=[
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
        [InlineKeyboardButton(text="ПВЗ Яндекс Маркет", callback_data="pickup:yandex")],
        [InlineKeyboardButton(text="ПВЗ OZON", callback_data="pickup:ozon")],
        [InlineKeyboardButton(text="Назад", callback_data="back_step_user:return_copies")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)
