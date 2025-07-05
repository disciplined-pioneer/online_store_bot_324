import re
from aiogram import Router, F, types
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from ...core.bot import bot
from ...utils.user.order import *
from ...keyboards.user.pick_up_point import *
from ...templates.user.pick_up_point import *
from ...utils.user.pick_up_point import start_payment_handler
from ...integrations.nominatim.geolocation import get_address_nominatim


router = Router()


# Обработка выбранного пункта выдачи
@router.callback_query(F.data.startswith("pickup:"))
async def choice_pickup(callback: types.CallbackQuery, state: FSMContext):

    await state.set_state(None)
    pickup = callback.data.split(':')[1]
    await callback.message.edit_text(
        text=delivery_messages[pickup],
        reply_markup=phone_number_menu
    )
    await state.update_data(pickup=pickup)


# Обработка кнопки "Указать номер"
@router.callback_query(F.data == "enter_phone")
async def enter_phone(callback: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    pickup = data.get('pickup')

    await callback.message.edit_text(
        text=enter_phone_messages,
        reply_markup=previous_stepn_keyboard(f'pickup:{pickup}')
    )
    await state.set_state(OrderDetailsStates.phone_number)


# Обработка ввода номера телефона
@router.message(OrderDetailsStates.phone_number)
async def process_phone_number(message: types.Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    pickup = data.get('pickup')
    last_id_message = data.get('last_id_message')
    phone = message.text.strip()

    try:
        if not re.match(PHONE_REGEX, phone):
            new_msg = await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=error_phone_message,
                reply_markup=previous_stepn_keyboard(f'pickup:{pickup}')
            )
            await state.update_data(last_id_message=new_msg.message_id)
            return
    except:
        return

    # Если номер валиден, сохраняем и двигаемся дальше
    await state.update_data(phone_number=phone)

    if pickup == 'ozon':
        
        new_msg = await bot.edit_message_text(
            chat_id=message.from_user.id,
            message_id=last_id_message,
            text=city_request_text,
            reply_markup=previous_stepn_keyboard(f'enter_phone')
        )
        await state.set_state(OrderDetailsStates.city)
        await state.update_data(last_id_message=new_msg.message_id)

    elif pickup == 'yandex':
        
        new_msg = await message.answer(
            text=format_phone_geolocation_text(phone),
            reply_markup=send_location_menu
        )
        await state.set_state(OrderDetailsStates.geolocation)
        await state.update_data(last_id_message=new_msg.message_id)
        await bot.delete_message(chat_id=message.from_user.id, message_id=last_id_message)


# Обработка гелолокации
@router.message(OrderDetailsStates.geolocation)
async def process_geolocation(message: Message, state: FSMContext):

    await message.delete()
    data = await state.get_data()
    last_id_message = data.get('last_id_message')

    location = message.location
    if not location:
        new_msg = await message.answer(
            text=geolocation_required_text,
            reply_markup=send_location_menu
        )
        await state.update_data(last_id_message=new_msg.message_id)
        await bot.delete_message(chat_id=message.from_user.id, message_id=last_id_message)
        return

    # Получаем адрес по координатам
    lat, lon = location.latitude, location.longitude
    address_data = await get_address_nominatim(lat, lon)
    if "error" in address_data:
        await message.answer(f"❌ Ошибка: {address_data['error']}")
        return

    city = address_data.get("city") or "Неизвестно"
    street = address_data.get("street") or "Неизвестно"
    house = address_data.get("house") or "Неизвестно"

    # Отправка данных
    await state.set_state(None)
    user_address = f"{city}, {street}, д. {house}"
    new_msg = await message.answer(
        text=build_user_address_text(user_address),
        reply_markup=await create_edit_geolocation_keyboard(bot)
    )
    await bot.delete_message(chat_id=message.from_user.id, message_id=last_id_message)

    # Сохраняем адрес
    await state.update_data(
        last_id_message=new_msg.message_id,
        geolocation={'city': city, 'street': street, 'house': house}
    )


# Обработка выбора редактирования
@router.callback_query(F.data.startswith("edit_geolocation:"))
async def alternative_back(callback: types.CallbackQuery, state: FSMContext):

    what_edit = callback.data.split(':')[1]
    await callback.message.edit_text(
        text=edit_address_prompts_text[what_edit],
        reply_markup=previous_stepn_keyboard('alternative_back:edit_geolocation')
    )
    await state.update_data(what_edit=what_edit)
    await state.set_state(OrderDetailsStates.geolocation_edit)


# Обработка редактирования адреса
@router.message(OrderDetailsStates.geolocation_edit)
async def geolocation_edit(message: Message, state: FSMContext):
    
    await message.delete()
    data = await state.get_data()

    what_edit = data.get('what_edit')  # city, street, house
    geolocation = data.get('geolocation', {})
    last_id_message = data.get('last_id_message')
    user_input = message.text.strip()

    # Выбор регулярки по типу поля
    try:
        if what_edit == "city":
            pattern = CITY_REGEX
        elif what_edit == "street":
            pattern = STREET_REGEX
        elif what_edit == "house":
            pattern = HOUSE_REGEX
        else:
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text="❌ Неверный тип редактируемого поля",
                reply_markup=previous_stepn_keyboard('alternative_back:edit_geolocation')
            )
            return

        # Проверка соответствия
        if not re.fullmatch(pattern, user_input):
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=INVALID_INPUT_MESSAGES[what_edit],
                reply_markup=previous_stepn_keyboard('alternative_back:edit_geolocation')
            )
            return
    except:
        return

    # Обновление данных и сообщение об успехе
    geolocation[what_edit] = user_input
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=last_id_message,
        text=get_value_changed_text(user_input),
        reply_markup=previous_stepn_keyboard('alternative_back:edit_geolocation')
    )
    await state.set_state(None)
    await state.update_data(geolocation=geolocation)


# Обработка ввода города
@router.message(OrderDetailsStates.city)
async def process_city(message: types.Message, state: FSMContext):

    # Данные
    await message.delete()
    data = await state.get_data()
    last_id_message = data.get('last_id_message')
    city = message.text.strip()

    try:
        if not re.match(CITY_REGEX, city):
            await bot.edit_message_text(
                chat_id=message.from_user.id,
                message_id=last_id_message,
                text=invalid_city_name_text,
                reply_markup=previous_stepn_keyboard(f'enter_phone')
            )
            return
    except:
        return

    # Отправляем сообщение
    await state.set_state(None)
    await state.update_data(geolocation={'city': city})
    await bot.edit_message_text(
        chat_id=message.from_user.id,
        message_id=last_id_message,
        text=user_city_text(city),
        reply_markup=await final_menu_keyb(bot)
    )


# Обработка кнопки "Всё верно"
@router.callback_query(F.data == "everything_correct")
async def edit_geolocation(callback: types.CallbackQuery, state: FSMContext):
    
    # Данные
    data = await state.get_data()
    pickup = data.get('pickup')
    tg_id = callback.from_user.id
    all_price = data.get('all_price', 1)

    if pickup == 'ozon':
        await callback.message.edit_text(
            text=generate_order_message(all_price),
            reply_markup=await start_payment_handler(user_id=tg_id, amount=all_price, order_data=data)
        )

    elif pickup == 'yandex':
        await callback.message.edit_text(
            text=generate_simple_message(all_price),
            reply_markup=await start_payment_handler(user_id=tg_id, amount=all_price, order_data=data)
        )
    await state.update_data(all_price=all_price)


# Назад к выбору пункта выдачи
@router.callback_query(F.data.startswith("alternative_back:"))
async def alternative_back(callback: types.CallbackQuery, state: FSMContext):

    await state.set_state(None)
    data = await state.get_data()
    type_choice = callback.data.split(':')[1]
    
    if type_choice == 'selection_pick-up_point':
        await callback.message.edit_text(
            text=choose_delivery_method_text,
            reply_markup=delivery_pickup_menu
        )

    elif type_choice == 'choice_city':
        await callback.message.edit_text(
            text=city_request_text,
            reply_markup=previous_stepn_keyboard(f'enter_phone')
        )
        await state.set_state(OrderDetailsStates.city)

    elif type_choice == 'edit_geolocation':
        geolocation = data.get('geolocation')
        city = geolocation.get("city") or "Неизвестно"
        street = geolocation.get("street") or "Неизвестно"
        house = geolocation.get("house") or "Неизвестно"
        user_address = f"{city}, {street}, д. {house}"
        await callback.message.edit_text(
            text=build_user_address_text(user_address),
            reply_markup=await create_edit_geolocation_keyboard(bot)
        )