import asyncio
import logging

from aiogram import Bot, Dispatcher

import utils
from handlers import router
from models import async_model_main

from settings import BOT_TOKEN


async def main():
    await async_model_main()

    bot = Bot(BOT_TOKEN)
    dp = Dispatcher()
    dp.include_router(router)
    rsi_task = asyncio.create_task(utils.handle_notifications(bot))
    dp_task = asyncio.create_task(dp.start_polling(bot))

    await asyncio.gather(rsi_task, dp_task)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.error("Bot stopped!")
