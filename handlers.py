from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import models
from keyboards import start_keyboard, notification_settings_menu

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    await models.insert_user_if_not_exist(message)
    await message.reply(f'Приветствую тебя! Начнем?', reply_markup=start_keyboard)


@router.callback_query(F.data == 'notification_settings')
async def notification_settings(callback: CallbackQuery):
    await callback.message.reply(text='Настройки уведомлений', reply_markup=notification_settings_menu)


@router.callback_query(F.data == 'notification_on')
async def notification_on(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    await models.update_notifications_status(telegram_id, True)
    await callback.message.reply(text='Уведомления включены\U0001F514')


@router.callback_query(F.data == 'notification_off')
async def notification_off(callback: CallbackQuery):
    telegram_id = callback.from_user.id
    await models.update_notifications_status(telegram_id, False)
    await callback.message.reply(text='Уведомления выключены\U0001F515')
