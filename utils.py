import asyncio
import os

import numpy
import requests
import talib
from binance.client import Client
from dotenv import load_dotenv

import models

load_dotenv()

API = os.environ.get("API")
SECRET_KEY = os.environ.get("SECRET_KEY")
client = Client(API, SECRET_KEY)


def get_klines_data(symbol, interval, limit):
    url = 'https://www.binance.com/api/v3/klines'
    params = {
        'symbol': symbol,
        'interval': interval,
        'limit': limit
    }
    response = requests.get(url=url, params=params)
    klines_data = []

    for kline in response.json():
        klines_data.append(float(kline[4]))

    return numpy.array(klines_data)


async def get_rci(symbol, interval, limit):
    data = get_klines_data(symbol, interval, limit)
    rsi = talib.RSI(data, 7)[-1]
    return rsi


async def send_notification(bot):
    is_buy = False
    is_sell = False

    while True:
        rsi = await get_rci("BTCUSDT", "15m", 200)
        print(rsi)
        if (rsi <= 30 and not is_buy) or (rsi >= 70 and not is_sell):
            users = await models.select_all_users()
            for user in users:
                if not user.is_notifications:
                    continue

                if rsi <= 30 and not is_buy:
                    is_buy = True
                    message = f"""BTCUSDT. Текущий RSI: ~{rsi:.2f}"""
                    await bot.send_message(user.telegram_id, message)

                if rsi >= 70 and not is_sell:
                    is_sell = True
                    message = f"""BTCUSDT. Текущий RSI: ~{rsi:.2f}"""
                    await bot.send_message(user.telegram_id, message)

        await asyncio.sleep(2)
