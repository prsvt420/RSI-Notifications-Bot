import asyncio
import logging

from aiogram import Bot, Dispatcher

from handlers import router

from settings import BOT_TOKEN


async def main():
    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error("Bot stopped!")
