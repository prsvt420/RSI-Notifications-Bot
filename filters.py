from aiogram.filters import BaseFilter
from aiogram.types import CallbackQuery

import models
from keyboards import buy_subscription


class IsUserSubscribed(BaseFilter):

    async def __call__(self, callback: CallbackQuery):
        telegram_id = callback.from_user.id
        is_subscribed = await models.is_user_subscribed(telegram_id)

        if is_subscribed:
            return True
        await callback.message.reply('У вас нет подписки на уведомления!', reply_markup=buy_subscription)
        return False


class IsAdmin(BaseFilter):

    async def __call__(self, callback: CallbackQuery):
        telegram_id = callback.from_user.id
        is_admin = await models.is_user_admin(telegram_id)

        return is_admin


class IsUserExist(BaseFilter):

    async def __call__(self, callback: CallbackQuery):
        telegram_id = callback.from_user.id

        await models.insert_user_is_not_exist(telegram_id)
        await models.insert_subscribed_is_not_exist(telegram_id)

        return True
