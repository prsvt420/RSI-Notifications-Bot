from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

start_keyboard = InlineKeyboardBuilder().add(
    InlineKeyboardButton(text='Управление уведомлениями\U0001F514', callback_data='notification_settings')
).as_markup()
