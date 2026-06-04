from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.main_menu_kb import main_menu_kb
from dbase.admin_db import is_seller
from dbase.users_db import add_user
from config import ADMIN_ID

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    await message.answer(
        "🎣 Привет!\n\n"
        "Данный бот, на основе данных погодных условий и фаз луны, даёт рекомендации, будет сегодня хороший клёв или плохой."
        "Конечно клёв зависит и от многих других факторов."
        "Но он поможет при выборе ехать на шашлыки или на рыбалку,"
        "Также, здесь вы найдёте полезные ссылки, которые помогут вам немного сохранить времени",
        reply_markup=main_menu_kb(
            is_admin=message.from_user.id == ADMIN_ID,
            is_seller=is_seller(message.from_user.id)
        )
    )
