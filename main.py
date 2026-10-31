"""Головний модуль запуску Telegram-бота тестування з Python.

Ініціалізує екземпляри Bot та Dispatcher, підключає маршрутизатори (роутери),
налаштовує логування та запускає Long Polling.
"""

import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, validate_config
from handlers import quiz_router


async def main() -> None:
    """Точка входу в програму."""
    # Налаштування формату логування
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger(__name__)

    # Перевірка наявності токена
    validate_config()

    logger.info("Ініціалізація Telegram-бота...")

    # Ініціалізація бота з HTML розміткою за замовчуванням
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )

    # Ініціалізація диспетчера зі сховищем станів у пам'яті (MemoryStorage)
    dp = Dispatcher(storage=MemoryStorage())

    # Реєстрація роутера
    dp.include_router(quiz_router)

    # Пропуск накопичених повідомлень, коли бот був офлайн
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Бот успішно запущений і готовий до роботи (Long Polling)!")
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        logger.info("Сесію бота завершено.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот зупинений користувачем.")
