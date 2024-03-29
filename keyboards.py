from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

start_keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Начнем\U000026A1', callback_data='menu')],
])

menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подписка на уведомления\U0001F451', callback_data='subscribe_notifications')],
    [InlineKeyboardButton(text='Меню уведомлений\U0001F4DC', callback_data='notifications_menu')],
])

subscribe_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Назад\U0001F519', callback_data='menu')],
    [InlineKeyboardButton(text='Продлить подписку\U0001F680', url='https://t.me/prsvt420')],
])

notifications_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Управление уведомлениями\U0001F514', callback_data='notifications_settings')],
    [InlineKeyboardButton(
        text='Список ваших уведомлений\U0001F4DD', callback_data='user_notifications_list'
    )],
    [InlineKeyboardButton(text='Добавить новое уведомление\U0001F514', callback_data='add_new_notification')],
    [InlineKeyboardButton(text='Назад\U0001F519', callback_data='menu')],
])

notifications_settings_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Включить уведомления\U0001F514', callback_data='notifications_on')],
    [InlineKeyboardButton(text='Выключить уведомления\U0001F515', callback_data='notifications_off')],
    [InlineKeyboardButton(text='Назад\U0001F519', callback_data='notifications_menu')],
])

notification_settings_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Включить уведомление\U0001F514', callback_data='notification_on')],
    [InlineKeyboardButton(text='Выключить уведомление\U0001F515', callback_data='notification_off')],
    [InlineKeyboardButton(text='Назад\U0001F519', callback_data='user_notifications_list')],
])

buy_subscription = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продлить подписку\U0001F680', url='https://t.me/prsvt420')]
])


async def create_buttons_for_user_notifications(notifications):
    inline_keyboard = []
    row = []

    for index, notification in enumerate(notifications):
        inline_keyboard_button = InlineKeyboardButton(text=str(index + 1), callback_data=str(index))
        row.append(inline_keyboard_button)

        if len(row) == 4 or index == len(notifications) - 1:
            inline_keyboard.append(row)
            row = []

    inline_keyboard.append([InlineKeyboardButton(text='Назад\U0001F519', callback_data='notifications_menu')])
    reply_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)

    return reply_keyboard_markup
