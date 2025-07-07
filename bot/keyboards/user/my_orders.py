from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_orders_keyboard(current_index: int, total: int) -> InlineKeyboardMarkup:
    row_1 = []
    row_2 = []
    row_3 = []
    row_4 = []

    is_first = current_index == 1
    is_last = current_index == total

    if not is_first:
        row_1.append(InlineKeyboardButton(
            text="⬅️ Назад",
            callback_data=f"user_orders:{current_index - 1}"
        ))

    if not is_first and not is_last:
        row_1.append(InlineKeyboardButton(
            text=f"{current_index}/{total}",
            callback_data="numbering"
        ))

    if not is_last:
        row_1.append(InlineKeyboardButton(
            text="Вперёд ➡️",
            callback_data=f"user_orders:{current_index + 1}"
        ))

    if is_first or is_last:
        row_2.append(InlineKeyboardButton(
            text=f"{current_index}/{total}",
            callback_data="numbering"
        ))

    row_4.append(InlineKeyboardButton(
        text="🔙 Меню",
        callback_data="back_menu"
    ))

    keyboard = [row_1]
    if row_2:
        keyboard.append(row_2)
    keyboard.append(row_3)
    keyboard.append(row_4)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
