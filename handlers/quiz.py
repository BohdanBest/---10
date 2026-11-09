import html
import random
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import List, Dict, Any

from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from data.questions import QUESTIONS_POOL, QuestionItem
from keyboards.quiz_kb import get_question_keyboard, get_restart_keyboard
from states.quiz_state import QuizStates

router = Router(name="quiz_router")


def get_current_kyiv_time() -> datetime:
    try:
        return datetime.now(ZoneInfo("Europe/Kyiv"))
    except Exception:
        return datetime.now()


def prepare_quiz_session() -> List[Dict[str, Any]]:
    total_to_take = min(10, len(QUESTIONS_POOL))
    chosen_raw = random.sample(QUESTIONS_POOL, total_to_take)

    prepared: List[Dict[str, Any]] = []
    for item in chosen_raw:
        shuffled_options = list(item["options"])
        random.shuffle(shuffled_options)

        prepared.append({
            "id": item["id"],
            "question": item["question"],
            "options": shuffled_options,
            "correct_answer": item["correct_answer"],
            "explanation": item["explanation"],
        })
    return prepared


async def send_question(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    q_index: int = data.get("current_index", 0)
    questions: List[Dict[str, Any]] = data.get("questions", [])

    if q_index >= len(questions):
        await finish_quiz(message, state)
        return

    q = questions[q_index]
    total_q = len(questions)

    text = (
        f"<b>Питання {q_index + 1} з {total_q}:</b>\n\n"
        f"❓ <b>{html.escape(q['question'])}</b>"
    )

    kb = get_question_keyboard(q["options"])
    await message.answer(text, reply_markup=kb)


@router.message(CommandStart())
async def handle_start(message: Message, state: FSMContext) -> None:
    await start_new_quiz(message, state)


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    help_text = (
        "🤖 <b>Бот-тестувальник знань з Python та ООП</b>\n\n"
        "• Для початку або перезапуску тесту надішліть команду /start\n"
        "• Тест складається з 10 випадкових запитань\n"
        "• До кожного питання пропонується 4 варіанти відповідей\n"
        "• Після кожної відповіді ви одразу побачите результат та пояснення\n"
        "• У кінці формується підсумковий звіт із балами, датою та часом проходження."
    )
    await message.answer(help_text)


async def start_new_quiz(message: Message, state: FSMContext) -> None:
    questions = prepare_quiz_session()
    now = get_current_kyiv_time()

    await state.set_state(QuizStates.answering)
    await state.set_data({
        "questions": questions,
        "current_index": 0,
        "score": 0,
        "start_timestamp": time.time(),
        "start_datetime_str": now.strftime("%d.%m.%Y %H:%M:%S"),
        "history": [],
    })

    intro_text = (
        "👋 <b>Вітаємо у тестуванні з Python та ООП!</b>\n\n"
        "Вам належить відповісти на <b>10 запитань</b>. "
        "Порядок питань та варіантів відповідей щоразу формується випадково.\n\n"
        "⏱ <i>Відлік часу розпочато. Бажаємо успіху!</i>"
    )
    await message.answer(intro_text)
    await send_question(message, state)


@router.callback_query(F.data.startswith("ans:"))
async def handle_answer(callback: CallbackQuery, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state != QuizStates.answering.state:
        await callback.answer("⚠️ Цей тест уже неактивний. Натисніть /start для нового проходження.", show_alert=True)
        return

    data = await state.get_data()
    q_index: int = data.get("current_index", 0)
    questions: List[Dict[str, Any]] = data.get("questions", [])

    if q_index >= len(questions):
        await callback.answer()
        return

    try:
        selected_idx = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка обробки відповіді.")
        return

    current_q = questions[q_index]
    selected_option = current_q["options"][selected_idx]
    correct_option = current_q["correct_answer"]
    is_correct = (selected_option == correct_option)

    score = data.get("score", 0) + (1 if is_correct else 0)
    history = data.get("history", [])
    history.append({
        "question": current_q["question"],
        "selected": selected_option,
        "correct": correct_option,
        "is_correct": is_correct,
    })

    if is_correct:
        feedback = (
            f"✅ <b>Правильно!</b>\n"
            f"💡 <i>{html.escape(current_q['explanation'])}</i>"
        )
    else:
        feedback = (
            f"❌ <b>Неправильно!</b>\n"
            f"Ваша відповідь: <s>{html.escape(selected_option)}</s>\n"
            f"Правильна відповідь: <b>{html.escape(correct_option)}</b>\n\n"
            f"💡 <i>{html.escape(current_q['explanation'])}</i>"
        )

    await callback.answer("Відповідь прийнято!")

    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(feedback)

    next_index = q_index + 1
    await state.update_data(
        current_index=next_index,
        score=score,
        history=history,
    )

    if next_index < len(questions):
        await send_question(callback.message, state)
    else:
        await finish_quiz(callback.message, state)


async def finish_quiz(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    score: int = data.get("score", 0)
    questions: List[Dict[str, Any]] = data.get("questions", [])
    total_q = len(questions) if questions else 10
    start_ts: float = data.get("start_timestamp", time.time())
    start_date_str: str = data.get("start_datetime_str", get_current_kyiv_time().strftime("%d.%m.%Y %H:%M:%S"))
    history: List[Dict[str, Any]] = data.get("history", [])

    elapsed_seconds = max(1, int(time.time() - start_ts))
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    if minutes > 0:
        duration_str = f"{minutes} хв {seconds} с"
    else:
        duration_str = f"{seconds} с"

    percentage = int((score / total_q) * 100) if total_q > 0 else 0

    if percentage >= 90:
        badge = "🏆 Відмінно! Глибоке розуміння Python та ООП!"
    elif percentage >= 70:
        badge = "👍 Добре! Солідний рівень знань."
    elif percentage >= 50:
        badge = "👌 Задовільно. Є над чим попрацювати."
    else:
        badge = "📚 Потрібно підтягнути теоретичний матеріал."

    details_lines = []
    for idx, item in enumerate(history, 1):
        status_icon = "✅" if item["is_correct"] else "❌"
        short_q = item["question"]
        if len(short_q) > 60:
            short_q = short_q[:57] + "..."
        details_lines.append(f"{idx}. {status_icon} {html.escape(short_q)}")

    details_text = "\n".join(details_lines)

    report_text = (
        "🏁 <b>Тестування завершено!</b>\n\n"
        f"📊 <b>Результат:</b> <code>{score} / {total_q}</code> ({percentage}%)\n"
        f"📅 <b>Дата тестування:</b> {start_date_str}\n"
        f"⏱ <b>Тривалість:</b> {duration_str}\n\n"
        f"<b>Вердикт:</b> {badge}\n\n"
        f"<b>Детальний звіт за запитаннями:</b>\n"
        f"{details_text}\n\n"
        "Щоб покращити свій результат або пройти інші випадкові питання, натисніть кнопку нижче:"
    )

    await state.clear()
    await message.answer(report_text, reply_markup=get_restart_keyboard())


@router.callback_query(F.data == "restart_quiz")
async def handle_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await start_new_quiz(callback.message, state)
