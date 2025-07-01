from settings import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

examples_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Картины на металле", callback_data="viewing:pictures")],
        [InlineKeyboardButton(text="Индивидуальная гравировка", callback_data="viewing:engraving")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

# Клавиатура с пагинацией
def create_pagination_keyboard(category: str, current_index: int, total: int) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для навигации по примерам:
    """

    row_1 = []
    row_2 = []
    row_3 = []

    # Кнопка "Назад"
    if current_index > 1:
        row_1.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"{category}:{current_index - 1}"
        ))

    # Кнопка "Следующий пример"
    if current_index < total:
        row_1.append(InlineKeyboardButton(
            text="➡️ Вперёд",
            callback_data=f"{category}:{current_index + 1}"
        ))

    # Кнопка "Примеры работ" — возврат к списку категорий
    row_2.append(InlineKeyboardButton(
        text="Примеры работ",
        callback_data="examples"
    ))

    # Кнопка "Меню" — возврат к пункту 1
    row_3.append(InlineKeyboardButton(
        text="🔙 Меню",
        callback_data="start"
    ))

    return InlineKeyboardMarkup(inline_keyboard=[row_1, row_2, row_3])