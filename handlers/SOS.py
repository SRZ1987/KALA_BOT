from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from utils.fsm import SOSState
from keyboards.SOS_kb import contact_geo_kb
from keyboards.back_kb import back_kb
from dbase.data_dase import all_users

import asyncio

router = Router()

print("USERS:", all_users)


async def broadcast_sos(bot, text: str, users: list[int], lat=None, lon=None):
    for user_id in users:
        try:
            # 🆘 текст SOS
            await bot.send_message(user_id, text)

            # 📍 КАРТА (ВАЖНО — это то, что тебе нужно)
            if lat is not None and lon is not None:
                await bot.send_location(
                    chat_id=user_id,
                    latitude=lat,
                    longitude=lon
                )

            await asyncio.sleep(0.05)

            # 🏠 кнопка назад
            await bot.send_message(
                user_id,
                "Вернуться в главное меню",
                reply_markup=back_kb()
            )

        except:
            continue


@router.callback_query(F.data == "sos_start")
async def sos_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SOSState.problem)
    await callback.message.answer("Опиши проблему:")


@router.message(SOSState.problem)
async def get_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(SOSState.location)

    await message.answer(
        "Отправь геолокацию 📍",
        reply_markup=contact_geo_kb()
    )


@router.message(SOSState.location)
async def get_location(message: Message, state: FSMContext):

    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
    else:
        lat = None
        lon = None

    await state.update_data(lat=lat, lon=lon)
    await state.set_state(SOSState.phone)

    await message.answer("Теперь отправь номер телефона 📱")


@router.message(SOSState.phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text or "не указан"

    text = (
        "🆘 SOS\n\n"
        f"Проблема: {data.get('problem')}\n"
        f"Телефон: {phone}"
    )

    await state.clear()

    await message.answer(
        "SOS отправлен!",
        reply_markup=ReplyKeyboardRemove()
    )

    # 🚀 ВАЖНО: передаём координаты отдельно
    await broadcast_sos(
        message.bot,
        text,
        list(all_users),
        lat=data.get("lat"),
        lon=data.get("lon")
    )

    print("USERS:", all_users)