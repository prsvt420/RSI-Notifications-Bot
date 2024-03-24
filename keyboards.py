from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_keyboard = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text='Управление уведомлениями\U0001F514', callback_data='notification_settings')
).as_markup()


notification_settings_menu = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text='\U0001F514', callback_data='notification_on'),
    InlineKeyboardButton(text='\U0001F515', callback_data='notification_off'),
).as_markup()
