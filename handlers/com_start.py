
from aiogram import Router, F
from aiogram.types import Message
router = Router()
from aiogram.filters import Command
from keyboards.main_menu_kb import main_menu_kb
from dbase.data_dase import all_users



@router.message(Command("start"))
async def cmd_start(message: Message):

    all_users.add(message.from_user.id)

    await message.answer(
        "🎣 Привет!\n\n"
        "Данный бот, на основе данных погодных условий и фаз луны, даёт рекомендации, будет сегодня хороший клёв или плохой."
        "Конечно клёв зависит и от многих других факторов."
        "Но он поможет при выборе ехать на шашлыки или на рыбалку,"
        "Также, здесь вы найдёте полезные ссылки, которые помогут вам немного сохранить времени",
        reply_markup=main_menu_kb()
    )
    print("FILE USERS OBJECT:", id(all_users))
    all_users.add(message.from_user.id)
    print("AFTER ADD:", all_users)
    print("OBJECT ID:", id(all_users))
