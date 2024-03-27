import asyncio
import os

import numpy
import aiohttp
import talib
from binance.client import Client
from dotenv import load_dotenv

import models

load_dotenv()

API = os.environ.get("API")
SECRET_KEY = os.environ.get("SECRET_KEY")
client = Client(API, SECRET_KEY)
sent_notifications = set()


async def get_klines_data(symbol, interval, limit):
    url = 'https://www.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url=url, params=params) as response:
            response_data = await response.json()

            klines_data = [float(kline[4]) for kline in response_data]

            return numpy.array(klines_data)


async def get_rci(symbol, interval, limit):
    data = await get_klines_data(symbol, interval, limit)
    rsi = talib.RSI(data, 7)[-1]
    return rsi


async def handle_notifications(bot):
    asyncio.create_task(clear_old_notifications())

    while True:
        notifications = await models.select_notifications()

        for notification in notifications:
            users = await models.select_users_by_notification_id(notification.id)

            if users:
                await send_notification_to_users(bot, users, notification)

        await asyncio.sleep(2)


async def send_notification_to_users(bot, users, notification):
    for user in users:
        symbol = notification.symbol
        interval = notification.interval
        user_telegram_id = user.telegram_id

        if (user_telegram_id, symbol) not in sent_notifications:
            rsi_by_symbol = await get_rci(symbol, interval, 200)
            is_overbought_oversold = (rsi_by_symbol <= 30 or rsi_by_symbol >= 70)

            if is_overbought_oversold:

                if rsi_by_symbol <= 30:
                    message = f"""Oversold |{symbol}. Текущий RSI: ~{rsi_by_symbol:.2f}"""
                    await bot.send_message(user_telegram_id, message)

                if rsi_by_symbol >= 70:
                    message = f"""Overbought | {symbol}. Текущий RSI: ~{rsi_by_symbol:.2f}"""
                    await bot.send_message(user_telegram_id, message)

                sent_notifications.add((user_telegram_id, symbol))


async def clear_old_notifications():
    while True:
        await asyncio.sleep(900)
        sent_notifications.clear()


async def russian_unit_handler(interval):
    number = interval[:-1]
    unit = interval[-1]

    russian_unit = {
        'м': 'm',
        'ч': 'h',
        'М': 'M',
        'д': 'd',
        'н': 'w',
    }

    if unit in russian_unit:
        unit = russian_unit[unit]

    return number + unit
