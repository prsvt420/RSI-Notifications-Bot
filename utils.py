import asyncio

import aiohttp
import numpy
import talib
from binance.client import Client

import models

client = Client()
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
    rsi = talib.RSI(data, 14)[-1]
    return rsi


async def handle_notifications(bot):

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
        rsi_by_symbol = await get_rci(symbol, interval, 200)
        rsi_status = await get_rsi_status(rsi_by_symbol)

        if not rsi_status or (user_telegram_id, interval, symbol, rsi_status) not in sent_notifications:
            message = await get_message_text(symbol, interval, rsi_by_symbol, rsi_status)
            if message:
                await bot.send_message(user_telegram_id, message)

            sent_notifications.add((user_telegram_id, interval, symbol, rsi_status))


async def get_message_text(symbol, interval, rsi, rsi_status):
    rsi_status = await get_rsi_status(rsi)
    rsi = round(rsi, 2)

    russian_text_interval = await get_interval_text(interval, 'ru')
    english_text_interval = await get_interval_text(interval, 'en')
    price_symbol = await get_price_symbol(symbol)

    status_emoji = ''

    if rsi_status == 'Overbought':
        status_emoji = '\U0001F4C8'
    elif rsi_status == 'Oversold':
        status_emoji = '\U0001F4C9'

    if rsi_status == 'Overbought' or rsi_status == 'Oversold':
        return (f'\U000026A1 Symbol: {symbol}\n'
                f'{status_emoji} Status: {rsi_status}\n'
                f'\U0001F4CA RSI: {rsi}\n'
                f'\U0001F4B8 Price: {price_symbol}$\n'
                f'\U0001F551 Interval: {english_text_interval} | {russian_text_interval}')


async def get_price_symbol(symbol):
    return round(float(client.get_symbol_ticker(symbol=symbol)['price']), 2)


async def get_rsi_status(rsi):
    rsi_status = ''

    if rsi >= 70:
        rsi_status = 'Overbought'
    elif rsi <= 30:
        rsi_status = 'Oversold'

    return rsi_status


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


async def get_interval_text(interval: str, language: str) -> str:
    intervals = {
        '1m': ('1 минута', '1 minute'),
        '3m': ('3 минуты', '3 minutes'),
        '5m': ('5 минут', '5 minutes'),
        '15m': ('15 минут', '15 minutes'),
        '30m': ('30 минут', '30 minutes'),
        '1h': ('1 час', '1 hour'),
        '2h': ('2 часа', '2 hours'),
        '4h': ('4 часа', '4 hours'),
        '6h': ('6 часов', '6 hours'),
        '8h': ('8 часов', '8 hours'),
        '12h': ('12 часов', '12 hours'),
        '1d': ('1 день', '1 day'),
        '3d': ('3 дня', '3 days'),
        '1w': ('1 неделя', '1 week'),
        '1M': ('1 месяц', '1 month'),
    }

    if language == 'ru':
        return intervals.get(interval, 'Интервал не найден')[0]
    elif language == 'en':
        return intervals.get(interval, 'Interval not found')[1]
