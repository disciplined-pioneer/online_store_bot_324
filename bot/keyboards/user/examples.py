from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

examples_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Картины на металле", callback_data="viewing:pictures")],
        [InlineKeyboardButton(text="Индивидуальная гравировка", callback_data="viewing:engraving")],
        [InlineKeyboardButton(text="🔙 Меню", callback_data="back_menu")]
    ]
)

# Клавиатура с пагинацией для примеров
def create_pagination_keyboard(category: str, current_index: int, total: int) -> InlineKeyboardMarkup:
    """
    Генерирует инлайн-клавиатуру для навигации по примерам:
    - Если элемент не первый и не последний, нумерация отображается между "Назад" и "Вперёд"
    - Если элемент первый или последний — нумерация отображается отдельной строкой
    """
    row_1 = []
    row_2 = []
    row_3 = []
    row_4 = []

    is_first = current_index == 1
    is_last = current_index == total

    # Кнопка "Назад"
    if not is_first:
        row_1.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"{category}:{current_index - 1}"
        ))

    # Нумерация между кнопками только если это не первое и не последнее изображение
    if not is_first and not is_last:
        row_1.append(InlineKeyboardButton(
            text=f"{current_index}/{total}",
            callback_data="numbering"
        ))

    # Кнопка "Вперёд"
    if not is_last:
        row_1.append(InlineKeyboardButton(
            text="Вперёд ➡️",
            callback_data=f"{category}:{current_index + 1}"
        ))

    # Если первое или последнее изображение — нумерация отдельной строкой
    if is_first or is_last:
        row_2.append(InlineKeyboardButton(
            text=f"{current_index}/{total}",
            callback_data="numbering"
        ))

    # Кнопка "Примеры работ"
    row_3.append(InlineKeyboardButton(
        text="Примеры работ",
        callback_data="examples"
    ))

    # Кнопка "Меню"
    row_4.append(InlineKeyboardButton(
        text="🔙 Меню",
        callback_data="back_menu:images"
    ))

    # Собираем клавиатуру
    keyboard = [row_1]
    if row_2:
        keyboard.append(row_2)
    keyboard.append(row_3)
    keyboard.append(row_4)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
