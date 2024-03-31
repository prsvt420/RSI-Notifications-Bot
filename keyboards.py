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

admin_inline_keyboard_button = [InlineKeyboardButton(text='Админ меню\U0001F6E1', callback_data='admin_menu')]

admin_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Продлить подписку пользователю\U0001F680', callback_data='to_extend_subscription')],
    [InlineKeyboardButton(text='Назад\U0001F519', callback_data='menu')],
])


async def create_buttons_for_user_notifications(page, total_pages, start_index, end_index, notifications):
    inline_keyboard = []
    row = []
    for index, notification in enumerate(notifications):
        index += start_index
        inline_keyboard_button = InlineKeyboardButton(text=str(index + 1), callback_data=str(index))
        row.append(inline_keyboard_button)

        if len(row) == 4 or index == end_index - 1:
            inline_keyboard.append(row)
            row = []

    await create_pagination_buttons(inline_keyboard, page, total_pages)
    inline_keyboard.append([InlineKeyboardButton(text='Назад\U0001F519', callback_data='notifications_menu')])
    reply_keyboard_markup = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    return reply_keyboard_markup


async def create_pagination_buttons(inline_keyboard, page, total_pages):
    if total_pages == 1:
        inline_keyboard.append([
            InlineKeyboardButton(text=' ', callback_data=' '),
            InlineKeyboardButton(
                text=f'{page}/{total_pages}',
                callback_data=f'user_notifications_list?page={page}'
            ),
            InlineKeyboardButton(text=' ', callback_data=' ')
        ])
    else:
        buttons = [
            InlineKeyboardButton(text='←', callback_data=f'user_notifications_list_prev?page={page}'),
            InlineKeyboardButton(
                text=f'{page}/{total_pages}',
                callback_data=f'user_notifications_list?page={page}'
            ),
            InlineKeyboardButton(text='→', callback_data=f'user_notifications_list_next?page={page}')
        ]
        if page == 1:
            buttons[0] = InlineKeyboardButton(text=' ', callback_data=' ')
        elif page == total_pages:
            buttons[2] = InlineKeyboardButton(text=' ', callback_data=' ')
        inline_keyboard.append(buttons)
