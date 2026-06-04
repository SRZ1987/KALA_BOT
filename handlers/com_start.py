from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from keyboards.main_menu_kb import main_menu_kb
from dbase.admin_db import is_seller
from dbase.users_db import add_user
from config import ADMIN_ID
from utils.menu_text import main_menu_text

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):

    add_user(
        message.from_user.id,
        message.from_user.first_name
    )

    is_admin = message.from_user.id == ADMIN_ID
    seller = is_seller(message.from_user.id)

    await message.answer(
        main_menu_text(
            is_admin=is_admin,
            is_seller=seller
        ),
        reply_markup=main_menu_kb(
            is_admin=is_admin,
            is_seller=seller
        )
    )
