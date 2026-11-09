"""Головний модуль запуску Telegram-бота тестування з Python.

Ініціалізує екземпляри Bot та Dispatcher, підключає маршрутизатори (роутери),
запускає легковиковий HTTP-сервер для health-check на безкоштовному тарифі Render
та запускає Long Polling.
"""

import asyncio
import logging
import os
import sys

from aiohttp import web
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN, validate_config
from handlers import quiz_router


async def health_check_handler(request: web.Request) -> web.Response:
    """HTTP endpoint для перевірки стану бота сервісом Render."""
    return web.Response(
        text="🤖 Telegram Python Quiz Bot is running smoothly on Render!",
        content_type="text/plain",
        status=200
    )


async def start_health_server(port: int, logger: logging.Logger) -> web.AppRunner:
    """Запускає вбудований aiohttp вебсервер для прив'язки до порту Render."""
    app = web.Application()
    app.router.add_get("/", health_check_handler)
    app.router.add_get("/health", health_check_handler)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host="0.0.0.0", port=port)
    await site.start()
    logger.info("Вбудований вебсервер успішно запущено на порту %d", port)
    return runner


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

    # Запуск легкого вебсервера для підтримки Free Web Service на Render
    # Render передає номер порту через змінну середовища PORT
    port = int(os.getenv("PORT", "10000"))
    runner = await start_health_server(port, logger)

    # Пропуск накопичених повідомлень, коли бот був офлайн
    await bot.delete_webhook(drop_pending_updates=True)

    logger.info("Бот успішно запущений і готовий до роботи (Long Polling)!")
    try:
        await dp.start_polling(bot)
    finally:
        await runner.cleanup()
        await bot.session.close()
        logger.info("Сесію бота завершено.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Бот зупинений користувачем.")
