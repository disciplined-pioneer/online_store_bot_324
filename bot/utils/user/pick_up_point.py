from ...keyboards.user.pick_up_point import payment_keyb
from ...integrations.yookassa.yookassa_payment import YookassaPayment

async def start_payment_handler(user_id: str, amount: float, order_data: dict):

    try:
        yk = YookassaPayment()
        payment_response = await yk.create(user_id, amount, order_data)

        if not payment_response:
            return payment_keyb()

        payment_url = payment_response.get("confirmation", {}).get("confirmation_url")
        if not payment_url:
            return payment_keyb()

        keyboard = payment_keyb(payment_url)
        return keyboard
    
    except:
        return payment_keyb()