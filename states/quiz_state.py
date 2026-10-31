"""Модуль станів FSM для керування сесією проходження тесту.
"""

from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    """Стани користувача під час складання тесту."""
    answering = State()  # Користувач перебуває в процесі відповідей на питання
