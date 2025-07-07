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
