import asyncio

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from dbase.admin_db import is_test_mode_enabled
from dbase.sos_db import add_sos_report
from dbase.users_db import all_users
from keyboards.SOS_kb import contact_kb, geo_kb
from keyboards.back_kb import back_kb, connection_back_kb
from utils.channel import get_content_channel_id
from utils.fsm import SOSState


router = Router()


async def broadcast_sos(bot, text: str, users: list[int], lat=None, lon=None):
    if is_test_mode_enabled():
        return

    for user_id in users:
        try:
            await bot.send_message(user_id, text)

            if lat is not None and lon is not None:
                await bot.send_location(
                    chat_id=user_id,
                    latitude=lat,
                    longitude=lon
                )

            await asyncio.sleep(0.05)

            await bot.send_message(
                user_id,
                "Вернуться в главное меню",
                reply_markup=back_kb()
            )

        except Exception:
            continue


async def publish_sos_to_channel(bot, text: str, lat=None, lon=None):
    channel_id = get_content_channel_id()

    if not channel_id:
        return False

    try:
        await bot.send_message(channel_id, text)

        if lat is not None and lon is not None:
            await bot.send_location(
                chat_id=channel_id,
                latitude=lat,
                longitude=lon
            )
    except Exception:
        return False

    return True


@router.callback_query(F.data == "sos_start")
async def sos_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SOSState.problem)
    await callback.message.edit_text(
        "Опиши проблему:",
        reply_markup=connection_back_kb()
    )
    await callback.answer()


@router.message(SOSState.problem)
async def get_problem(message: Message, state: FSMContext):
    await state.update_data(problem=message.text)
    await state.set_state(SOSState.location)

    await message.answer(
        "Отправь геолокацию или нажми Пропустить геолокацию.",
        reply_markup=geo_kb()
    )


@router.message(SOSState.location)
async def get_location(message: Message, state: FSMContext):
    if message.location:
        lat = message.location.latitude
        lon = message.location.longitude
    elif message.text == "Пропустить геолокацию":
        lat = None
        lon = None
    else:
        lat = None
        lon = None

    await state.update_data(lat=lat, lon=lon)
    await state.set_state(SOSState.phone)

    await message.answer(
        "Теперь нажми Телефон или напиши номер вручную.",
        reply_markup=contact_kb()
    )


@router.message(SOSState.phone)
async def get_phone(message: Message, state: FSMContext):
    data = await state.get_data()

    if message.contact:
        phone = message.contact.phone_number
    else:
        phone = message.text or "не указан"

    report = add_sos_report(
        message.from_user,
        data.get("problem"),
        phone,
        lat=data.get("lat"),
        lon=data.get("lon")
    )

    text = (
        f"SOS #{report['id']}\n\n"
        f"Проблема: {data.get('problem')}\n"
        f"Телефон: {phone}"
    )

    await state.clear()
    channel_sent = await publish_sos_to_channel(
        message.bot,
        text,
        lat=data.get("lat"),
        lon=data.get("lon")
    )

    await message.answer(
        (
            "SOS сохранен. Тестовый режим включен, личная рассылка отключена."
            if is_test_mode_enabled()
            else "SOS отправлен!"
        )
        + (
            "\nОпубликовано в канале."
            if channel_sent
            else "\nКанал не настроен, в канал не отправлено."
        ),
        reply_markup=ReplyKeyboardRemove()
    )

    await broadcast_sos(
        message.bot,
        text,
        list(all_users),
        lat=data.get("lat"),
        lon=data.get("lon")
    )
