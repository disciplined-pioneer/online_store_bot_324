from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_product_keyboard(category: str, current_index: int, total: int) -> InlineKeyboardMarkup:
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
    print(f"{category}:{current_index + 1}")
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

    # Кнопка Заказ"
    row_3.append(InlineKeyboardButton(
        text="Заказать",
        callback_data=f"order_confirm:{current_index}"
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