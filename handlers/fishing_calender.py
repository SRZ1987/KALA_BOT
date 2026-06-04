from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.city_keyboard import get_city_keyboard


router = Router()


@router.callback_query(F.data == "fishing_calender_main_menu")
async def show_forecast(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>Календарь клёва</b>\n\n"
        "Выбери ближайший город. Бот оценит погоду, давление, ветер и лунную фазу, "
        "а затем покажет прогноз клёва на сегодня или на неделю.",
        reply_markup=get_city_keyboard()
    )
    await callback.answer()
