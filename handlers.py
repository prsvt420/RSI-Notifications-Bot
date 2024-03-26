from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import keyboards
import models

router = Router()


@router.message(CommandStart())
async def bot_start(message: Message):
    await models.insert_user_if_not_exist(message)
    await message.reply(f'Приветствую тебя! Начнем?', reply_markup=keyboards.start_keyboard)


@router.callback_query(F.data == 'notifications_menu')
async def notifications_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.reply(text='Меню уведомлений\U0001F9FE', reply_markup=keyboards.notifications_menu)


@router.callback_query(F.data == 'notifications_settings')
async def notifications_settings(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.reply(
        text='Настройки уведомлений\U00002699', reply_markup=keyboards.notifications_settings_menu
    )


async def process_notifications_status_change(callback, status):
    await callback.answer('')
    telegram_id = callback.from_user.id
    await models.update_notifications_status(telegram_id, status)
    status_text = 'выключены\U0001F514' if not status else 'включены\U0001F515'
    await callback.message.reply(text=f'Уведомления {status_text}')


@router.callback_query(F.data == 'notifications_on')
async def notifications_on(callback: CallbackQuery):
    await process_notifications_status_change(callback, True)


@router.callback_query(F.data == 'notifications_off')
async def notifications_off(callback: CallbackQuery):
    await process_notifications_status_change(callback, False)


@router.callback_query(F.data == 'user_notifications_list')
async def user_notifications_list(callback: CallbackQuery):
    await callback.answer('')
    telegram_id = callback.from_user.id
    user_id = await models.select_user_id_by_telegram_id(telegram_id)
    notifications = await models.select_user_notifications_by_user_id(user_id)
    notifications_buttons = await keyboards.create_buttons_for_user_notifications(notifications)
    text = f'Ваши уведомления: \n' + '\n'.join(
        [f'{index}.  \U0001F4CC ' + str(notification) for index, notification in enumerate(notifications, start=1)]
    )
    await callback.message.reply(text=text, reply_markup=notifications_buttons)


@router.callback_query(F.data.isdigit())
async def button_notification_select(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.reply(text=f'Настройка уведомления {int(callback.data) + 1}\U00002699',
                                 reply_markup=keyboards.notification_settings_menu)


async def process_notification_status_change(callback, status):
    await callback.answer('')
    message_text = callback.message.text
    index = int(message_text[-2]) - 1
    telegram_id = callback.from_user.id
    user_id = await models.select_user_id_by_telegram_id(telegram_id)
    notifications = await models.select_user_notifications_by_user_id(user_id)
    selected_notification = notifications[index]
    selected_user_notification = await models.select_notification_by_user_id_and_notification_id(
        user_id,
        selected_notification.id
    )
    await models.update_user_notification_status(selected_user_notification, status)
    status_text = 'выключено\U0001F514' if not status else 'включено\U0001F515'
    await callback.message.reply(text=f'Уведомление {status_text}')


@router.callback_query(F.data == 'notification_on')
async def notification_off(callback: CallbackQuery):
    await process_notification_status_change(callback, True)


@router.callback_query(F.data == 'notification_off')
async def notification_off(callback: CallbackQuery):
    await process_notification_status_change(callback, False)
