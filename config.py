"""Модуль конфігурації проєкту.

Завантажує змінні середовища з файлу .env та валідує наявність обов'язкових
параметрів для запуску бота.
"""

import os
import sys
from dotenv import load_dotenv

# Завантаження змінних з .env файлу
load_dotenv()

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "").strip()

def validate_config() -> None:
    """Перевіряє коректність конфігурації перед стартом бота."""
    if not BOT_TOKEN:
        print(
            "ПОМИЛКА: Не вказано BOT_TOKEN!\n"
            "Будь ласка, створіть файл .env на основі .env.example та додайте токен від @BotFather:\n"
            "BOT_TOKEN=ваш_токен_тут",
            file=sys.stderr,
        )
        sys.exit(1)
