"""Модуль генерації інлайн-клавіатур для тестування.
"""

from typing import List
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_question_keyboard(options: List[str]) -> InlineKeyboardMarkup:
    """Створює клавіатуру з 4 варіантами відповіді (розміщення по 1 кнопці в рядку).

    Args:
        options: Перелік варіантів відповідей (вже перемішаних).

    Returns:
        Об'єкт InlineKeyboardMarkup.
    """
    builder = InlineKeyboardBuilder()
    letters = ["A", "B", "C", "D"]

    for i, option in enumerate(options):
        letter = letters[i] if i < len(letters) else f"{i+1}"
        builder.button(
            text=f"{letter}) {option}",
            callback_data=f"ans:{i}"
        )

    builder.adjust(1)
    return builder.as_markup()


def get_restart_keyboard() -> InlineKeyboardMarkup:
    """Повертає кнопку для повторного запуску тестування."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text="🔄 Пройти тест ще раз",
        callback_data="restart_quiz"
    )
    return builder.as_markup()
