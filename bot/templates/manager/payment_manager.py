def format_order_text(
    order_id: int,
    product_name: str,
    quantity: int,
    total_price: float,
    address: str,
    delivery_method: str,
    image_size: str,
    phone_number: str,
) -> str:
    text = (
        f"<b>Номер заказа:</b> {order_id:06d}\n"
        f"<b>Название товара:</b> {product_name}\n"
        f"<b>Количество:</b> {quantity}\n"
        f"<b>Стоимость:</b> {total_price} ₽\n"
        f"<b>Адрес доставки:</b> {address}\n"
        f"<b>Способ доставки:</b> {delivery_method}\n"
        f"<b>Размер картины:</b> {image_size}\n"
        f"<b>Номер телефона:</b> {phone_number}"
    )

    return text

def order_sent_msg(order_id: int) -> str:
    return f"✅ Ваш заказ №{order_id:06d} был отправлен!"

def user_notified_msg(user_id: int) -> str:
    return f"✅ Сообщение было отправлено пользователю {user_id}!"

def ozon_pickup_request_msg(order_id: int) -> str:
    return (
        f"Просьба зайти в приложение Ozon и выбрать удобный пункт для получения "
        f"заказа №{order_id:06d}. Срок доставки будет отражаться в приложении Ozon"
    )

def message_sent_msg(user_id: int) -> str:
    return f"✅ Сообщение было отправлено пользователю {user_id}!"

send_address_request_msg = "Отправьте актуальный адрес в группу!"

def address_updated_msg(order_id: int, address: str) -> str:
    return f'Актуальный адрес в заказе №{order_id:06d} был изменён на: "{address}"'

def address_update_confirm_msg(order_id: int, address: str, user_id: int) -> str:
    return f'✅ Актуальный адрес в заказе №{order_id:06d} был изменён на: "{address}". Сообщение было отправлено пользователю {user_id}!'

def files_uploading_msg(order_id: int) -> str:
    return f'📎 Загрузка файлов для заказа №{order_id:06d}...'
