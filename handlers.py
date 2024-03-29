import re

from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery

import keyboards
import models
import utils
from filters import IsUserSubscribed, IsAdmin
from utils import get_klines_data

router = Router()
is_new_notification = False
is_update_datetime_end_subscription = False
new_notification_pattern = r'^([А-ЯA-Za-z]+)\s*-\s*([0-9]+[mhMdwмчМдн])$'
extend_subscription_pattern = r'^[0-9]{10} - [0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}:[0-9]{2}$'


@router.message(CommandStart())
async def bot_start(message: Message):
    telegram_id = message.from_user.id
    await models.insert_user_is_not_exist(telegram_id)
    await models.insert_subscribed_is_not_exist(telegram_id)
    await message.reply(f'Приветствую тебя! Начнем?', reply_markup=keyboards.start_keyboard)


@router.callback_query(F.data == 'menu')
async def menu(callback: CallbackQuery):
    await callback.answer('')
    markup = keyboards.menu
    is_admin = await models.is_user_admin(callback.from_user.id)

    if is_admin:
        markup.inline_keyboard.extend(keyboards.admin_inline_keyboard_button)

    await callback.message.reply(text='Меню\U00002699', reply_markup=markup)


@router.callback_query(F.data == 'subscribe_notifications')
async def subscribe_notifications(callback: CallbackQuery):
    await callback.answer('')
    telegram_id = callback.from_user.id
    is_subscribed = await models.is_user_subscribed(telegram_id)
    subscription_end_datetime = await models.select_subscription_end_datetime_by_telegram_id(telegram_id)

    if is_subscribed:
        message = f'Подписка активна\U0001F48E\nОкончание подписки: {subscription_end_datetime}\U0000231B'
    else:
        message = 'Подписка не активна\U0000274C'

    await callback.message.reply(message, reply_markup=keyboards.subscribe_menu)


@router.callback_query(F.data == 'notifications_menu', IsUserSubscribed())
async def notifications_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.reply(text='Меню уведомлений\U0001F9FE', reply_markup=keyboards.notifications_menu)


@router.callback_query(F.data == 'notifications_settings', IsUserSubscribed())
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


@router.callback_query(F.data == 'notifications_on', IsUserSubscribed())
async def notifications_on(callback: CallbackQuery):
    await process_notifications_status_change(callback, True)


@router.callback_query(F.data == 'notifications_off', IsUserSubscribed())
async def notifications_off(callback: CallbackQuery):
    await process_notifications_status_change(callback, False)


@router.callback_query(F.data == 'user_notifications_list', IsUserSubscribed())
async def user_notifications_list(callback: CallbackQuery):
    await callback.answer('')
    telegram_id = callback.from_user.id
    user_id = await models.select_user_id_by_telegram_id(telegram_id)
    notifications = await models.select_user_notifications_by_user_id(user_id)
    notifications_buttons = await keyboards.create_buttons_for_user_notifications(notifications)
    text = f'Ваши уведомления: \n'
    for index, notification in enumerate(notifications):
        user_notification = await models.select_user_notification_by_user_id_and_notification_id(user_id,
                                                                                                 notification.id)
        russian_text_interval = await utils.get_interval_text(notification.interval, 'ru')
        english_text_interval = await utils.get_interval_text(notification.interval, 'en')
        status = '\U00002705' if user_notification.is_active else '\U0000274C'
        text += f'{index + 1}. {status} {notification.symbol} - {english_text_interval} | {russian_text_interval}\n'
    await callback.message.reply(text=text, reply_markup=notifications_buttons)


@router.callback_query(F.data.isdigit(), IsUserSubscribed())
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
    status_text = 'выключено\U0001F515' if not status else 'включено\U0001F514'
    await callback.message.reply(text=f'Уведомление {status_text}')


@router.callback_query(F.data == 'notification_on', IsUserSubscribed())
async def notification_off(callback: CallbackQuery):
    await process_notification_status_change(callback, True)


@router.callback_query(F.data == 'notification_off', IsUserSubscribed())
async def notification_off(callback: CallbackQuery):
    await process_notification_status_change(callback, False)


@router.callback_query(F.data == 'add_new_notification', IsUserSubscribed())
async def add_new_notification(callback: CallbackQuery):
    global is_new_notification
    is_new_notification = True
    await callback.answer('')
    await callback.message.reply(text='Введите новое уведомление в формате [SYMBOL - INTERVAL]')


@router.message(lambda message: re.match(new_notification_pattern, message.text), IsUserSubscribed())
async def new_notification_handler(message: Message):
    global is_new_notification

    if not is_new_notification:
        return

    symbol, interval = message.text.split('-')
    symbol, interval = symbol.strip().upper(), interval.strip()

    interval = await utils.russian_unit_handler(interval)

    try:
        is_exist_api = await get_klines_data(symbol, interval, 200)
        telegram_id = message.from_user.id
        user_id = await models.select_user_id_by_telegram_id(telegram_id)

        await models.insert_notification(symbol, interval)

        notification = await models.select_notification_by_symbol_and_interval(symbol, interval)
        answer = await models.insert_user_notification(notification.id, user_id)

        if answer:
            await message.reply(text='Уведомление добавлено\U00002699')
        else:
            await message.reply(text='Такое уведомление уже существует\U00002699')
    except IndexError:
        await message.reply(text='Такого символа или интервала не существует\U00002699')

    if_new_notification = False


@router.callback_query(F.data == 'admin_menu', IsAdmin())
async def admin_menu(callback: CallbackQuery):
    await callback.answer('')
    await callback.message.reply(text='Выберите действие', reply_markup=keyboards.admin_menu)


@router.callback_query(F.data == 'to_extend_subscription', IsAdmin())
async def to_extend_subscription(callback: CallbackQuery):
    global is_update_datetime_end_subscription

    is_update_datetime_end_subscription = True

    await callback.answer('')
    await callback.message.reply(
        text='Введите Telegram-ID и дату окончания подписки в формате [0123456789 - 2024-04-01 00:00:00]'
    )


@router.message(lambda message: re.match(extend_subscription_pattern, message.text), IsAdmin())
async def extend_subscription_handler(message: Message):
    global is_update_datetime_end_subscription

    try:
        telegram_id, subscription_end_datetime = message.text.split('-', 1)
        telegram_id, subscription_end_datetime = telegram_id.strip(), subscription_end_datetime.strip()
        await models.update_subscription_end_datetime(telegram_id, subscription_end_datetime)
        await message.reply(text='Подписка обновлена\U00002699')
    except ValueError:
        await message.reply(text='Был введен неверный формат\U00002699')

    is_update_datetime_end_subscription = False
