from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from keyboards import start_keyboard

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    await message.reply(f'Приветствую тебя! Начнем?', reply_markup=start_keyboard)
