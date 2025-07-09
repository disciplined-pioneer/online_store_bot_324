from ...db.models.models import OrderUsers

def format_order_text(order: OrderUsers) -> str:
    status = order.dispatch_status or "неизвестен"
    text = (
        f"🆔 Заказ ID: {order.id:06d}\n"  # ID с ведущими нулями до 6 знаков
        f"👤 Имя: {order.name or 'Не указано'}\n"
        f"💰 Цена: {order.price if order.price is not None else 'Не указана'}\n"
        f"📏 Размер: {order.image_size or '-'}\n"
        f"📄 Кол-во копий: {order.copies_count or '-'}\n"
        f"📞 Телефон: {order.phone_number or '-'}\n"
        f"🌍 Локация: {order.geolocation or '-'}\n"
        f"📁 Файл: {'есть' if order.file_id else 'нет'}\n"
        f"🚚 Статус отправки: {status}\n"
        f"⏰ Последнее обновление: {order.last_update.strftime('%d.%m.%Y %H:%M')}"
    )
    return text

no_orders_user = "У вас пока нет заказов"