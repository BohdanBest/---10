# ЗВІТ
### З лабораторної роботи №10
**з дисципліни:** «Fullstack розробка»  
**Тема:** «Розробка інтерактивного Telegram-бота для тестування знань з Python та ООП»  

---

## 1. Мета роботи
Ознайомитися з принципами роботи з бібліотеками для розробки ботів для месенджера Telegram. Розробити асинхронного Telegram-бота для тестування знань користувачів щодо синтаксису Python, особливостей ООП, стандартних бібліотек та типових конструкцій мови, реалізувавши механізми рандомізації, миттєвого зворотного зв'язку, підрахунку тривалості тестування та підготовки до хмарного розгортання.

---

## 2. Опис реалізованого функціоналу та архітектури програми

Для розробки було обрано сучасний асинхронний фреймворк **`aiogram 3.x`**, що є індустріальним стандартом у Python завдяки високій продуктивності, підтримці строгих типів (type hints) та вбудованому механізму FSM (Finite State Machine).

### Ключові особливості реалізації:
1. **Команда `/start`**: Ініціалізує нову сесію, генерує випадкову вибірку з 10 запитань та фіксує точний час початку тесту.
2. **Рандомізація**:
   * З пулу підготовлених запитань за допомогою `random.sample()` обирається 10 унікальних питань.
   * До кожного питання список із 4 варіантів відповідей перемішується (`random.shuffle()`), що унеможливлює механічне запам'ятовування розташування кнопок.
3. **Графічний інтерфейс через Inline-кнопки**:
   * Варіанти відповідей генеруються динамічно у вигляді `InlineKeyboardMarkup` (по одній кнопці на рядок із позначками A, B, C, D для максимальної ергономіки інтерфейсу).
4. **Миттєвий зворотний зв'язок (Feedback)**:
   * Одразу після натискання кнопки користувач отримує результат: `✅ Правильно!` або `❌ Неправильно!` із зазначенням правильної відповіді та теоретичним обґрунтуванням (explanation).
   * Попередня клавіатура очищується, що запобігає повторним натисканням або спотворенню статистики.
5. **Фінальна статистика та звіт**:
   * Кількість набраних балів (наприклад, `8 / 10`) та відсоток успішності;
   * Точна дата та час початку тестування (за часовим поясом `Europe/Kyiv`);
   * Точна тривалість проходження тесту (хвилини та секунди);
   * Текстовий вердикт успішності (оцінка рівня володіння мовою);
   * Повна історія відповідей за кожним питанням;
   * Кнопка `🔄 Пройти тест ще раз` для повторного проходження.
6. **Хмарне розгортання**:
   * Підготовлено конфігураційні файли `Procfile`, `runtime.txt`, `requirements.txt` та `render.yaml` для розгортання на хмарній платформі Render у форматі Background Worker (або Heroku).

---

## 3. Лістинг програми з детальними коментарями

### 3.1. `config.py` — Модуль конфігурації
```python
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
```

---

### 3.2. `data/questions.py` — Банк запитань з Python та ООП
```python
"""База тестових питань для Telegram-бота з мови Python та ООП.

Містить пул питань, кожен з яких має 4 варіанти відповіді, правильну відповідь
та коротке пояснення.
"""

from typing import TypedDict, List


class QuestionItem(TypedDict):
    id: int
    question: str
    options: List[str]
    correct_answer: str
    explanation: str


QUESTIONS_POOL: List[QuestionItem] = [
    {
        "id": 1,
        "question": "Який магічний метод в Python відповідає за створення нового екземпляра класу перед його ініціалізацією?",
        "options": [
            "__new__",
            "__init__",
            "__create__",
            "__call__"
        ],
        "correct_answer": "__new__",
        "explanation": "Метод `__new__` є конструктором об'єкта і відповідає за виділення пам'яті та створення екземпляра, тоді як `__init__` лише ініціалізує створений об'єкт."
    },
    {
        "id": 2,
        "question": "За яким алгоритмом Python вирішує порядок пошуку методів (MRO) при множинному успадкуванні?",
        "options": [
            "C3 Linearization",
            "Breadth-First Search (BFS)",
            "Depth-First Search (DFS)",
            "Dijkstra Algorithm"
        ],
        "correct_answer": "C3 Linearization",
        "explanation": "Починаючи з Python 2.3, для побудови MRO (Method Resolution Order) використовується алгоритм лінеаризації C3."
    },
    {
        "id": 3,
        "question": "Чим відрізняється метод з декоратором @classmethod від @staticmethod?",
        "options": [
            "@classmethod першим аргументом отримує клас (cls), а @staticmethod не має неявних аргументів",
            "@staticmethod першим аргументом отримує екземпляр (self), а @classmethod — ні",
            "@classmethod можна викликати лише без створення екземпляра, а @staticmethod — лише через екземпляр",
            "Вони ідентичні за функціоналом і є взаємозамінними синонімами"
        ],
        "correct_answer": "@classmethod першим аргументом отримує клас (cls), а @staticmethod не має неявних аргументів",
        "explanation": "`@classmethod` приймає `cls` як перший параметр і має доступ до стану класу, тоді як `@staticmethod` працює як звичайна функція, логічно зв'язана з класом."
    },
    {
        "id": 4,
        "question": "Що робить механізм 'Name Mangling' для атрибутів із двома підкресленнями (наприклад, __data)?",
        "options": [
            "Змінює внутрішнє ім'я атрибута на _ClassName__data для запобігання колізіям у нащадках",
            "Робить атрибут суворо недоступним на рівні інтерпретатора (Memory Error)",
            "Видаляє атрибут під час оптимізації байт-коду",
            "Автоматично створює для нього геттер і сеттер"
        ],
        "correct_answer": "Змінює внутрішнє ім'я атрибута на _ClassName__data для запобігання колізіям у нащадках",
        "explanation": "Name mangling перейменовує `__var` у `_ClassName__var`, захищаючи атрибут від випадкового перевизначення нащадками класу."
    },
    {
        "id": 5,
        "question": "Для чого використовується атрибут `__slots__` у класах Python?",
        "options": [
            "Для обмеження набору дозволених атрибутів та значної економії оперативної пам'яті",
            "Для автоматичного перетворення класу на абстрактний",
            "Для підтримки багатопотокового доступу до екземплярів без блокувань",
            "Для обов'язкового збереження об'єктів у базі даних"
        ],
        "correct_answer": "Для обмеження набору дозволених атрибутів та значної економії оперативної пам'яті",
        "explanation": "`__slots__` запобігає створенню внутрішнього словника `__dict__` для кожного екземпляра, зберігаючи значення у статичному масиві, що суттєво заощаджує пам'ять."
    },
    {
        "id": 6,
        "question": "Який результат виведе код: `print(type(type))`?",
        "options": [
            "<class 'type'>",
            "<class 'object'>",
            "<class 'class'>",
            "TypeError"
        ],
        "correct_answer": "<class 'type'>",
        "explanation": "У Python `type` є метакласом за замовчуванням, і він сам є екземпляром класу `type`."
    },
    {
        "id": 7,
        "question": "Яка проблема виникає при використанні змінного (mutable) об'єкта як значення за замовчуванням аргументу функції (наприклад, def f(x=[]))?",
        "options": [
            "Список створюється один раз при визначенні функції та зберігає стан між усіма викликами",
            "Виникає SyntaxError ще на етапі компіляції байт-коду",
            "Python генерує виняток RecursionError при другому виклику",
            "При кожному виклику список автоматично очищується"
        ],
        "correct_answer": "Список створюється один раз при визначенні функції та зберігає стан між усіма викликами",
        "explanation": "Значення за замовчуванням обчислюються один раз під час визначення (def), тому змінний об'єкт мутує між послідовними викликами."
    },
    {
        "id": 8,
        "question": "Яка різниця між операторами `==` та `is` в Python?",
        "options": [
            "`==` порівнює рівність значень (еквівалентність), а `is` перевіряє ідентичність об'єктів у пам'яті (id)",
            "`is` перевіряє типи даних, а `==` порівнює хеш-значення об'єктів",
            "`==` працює швидше, оскільки викликає id(), а `is` порівнює вміст",
            "Вони роблять те саме для всіх типів, крім None"
        ],
        "correct_answer": "`==` порівнює рівність значень (еквівалентність), а `is` перевіряє ідентичність об'єктів у пам'яті (id)",
        "explanation": "`==` викликає метод `__eq__` і порівнює значення, тоді як `is` перевіряє чи вказують дві змінні на одну й ту саму область пам'яті (`id(a) == id(b)`)."
    },
    {
        "id": 9,
        "question": "Які магічні методи повинен реалізувати об'єкт для підтримки протоколу контекстного менеджера (конструкція `with`)?",
        "options": [
            "__enter__ та __exit__",
            "__open__ та __close__",
            "__start__ та __stop__",
            "__before__ та __after__"
        ],
        "correct_answer": "__enter__ та __exit__",
        "explanation": "Протокол Context Manager в Python вимагає реалізації методів `__enter__` (виконується на вході) та `__exit__` (гарантовано виконується на виході)."
    },
    {
        "id": 10,
        "question": "Що повертає функція, яка містить ключове слово `yield` замість `return`?",
        "options": [
            "Об'єкт-генератор (generator object)",
            "Кортеж (tuple) усіх згенерованих значень",
            "None",
            "Список (list)"
        ],
        "correct_answer": "Об'єкт-генератор (generator object)",
        "explanation": "Наявність `yield` у тілі функції перетворює її на фабрику генераторів, яка повертає ітератор-генератор, зберігаючи свій стан між кроками."
    },
    {
        "id": 11,
        "question": "Що робить декоратор `functools.wraps` під час створення власного декоратора?",
        "options": [
            "Копіює метадані (ім'я функції, docstring тощо) з оригінальної функції в обгортку",
            "Прискорює виконання функції за рахунок JIT-компіляції",
            "Робить декоровану функцію асинхронною (корутиною)",
            "Запобігає рекурсивному виклику декоратора"
        ],
        "correct_answer": "Копіює метадані (ім'я функції, docstring тощо) з оригінальної функції в обгортку",
        "explanation": "Без `@functools.wraps(func)` обгорнута функція втрачає своє справжнє ім'я `__name__` та документацію `__doc__`, замінюючись даними wrapper-функції."
    },
    {
        "id": 12,
        "question": "Чим `copy.deepcopy()` відрізняється від поверхневого копіювання `copy.copy()`?",
        "options": [
            "deepcopy рекурсивно створює копії всіх вкладених об'єктів, розриваючи зв'язки з оригіналами",
            "deepcopy працює лише з примітивними типами чисел та рядків",
            "copy створює копію у файловій системі, а deepcopy — в оперативній пам'яті",
            "deepcopy змінює оригінальний об'єкт на незмінний (immutable)"
        ],
        "correct_answer": "deepcopy рекурсивно створює копії всіх вкладених об'єктів, розриваючи зв'язки з оригіналами",
        "explanation": "Поверхневе копіювання копіює лише зовнішній контейнер, залишаючи посилання на ті самі вкладені об'єкти; `deepcopy` копіює всю ієрархію об'єктів рекурсивно."
    },
    {
        "id": 13,
        "question": "Який базовий клас та декоратор зі стандартної бібліотеки Python використовуються для створення абстрактних класів?",
        "options": [
            "Модуль `abc`: клас `ABC` та декоратор `@abstractmethod`",
            "Модуль `typing`: клас `Generic` та `@abstract`",
            "Модуль `oop`: клас `Abstract` та `@interface`",
            "Модуль `builtins`: клас `Interface` та `@virtual`"
        ],
        "correct_answer": "Модуль `abc`: клас `ABC` та декоратор `@abstractmethod`",
        "explanation": "У Python створення абстрактних базових класів реалізується через модуль `abc` (Abstract Base Classes) з використанням `ABC` та декоратора `@abstractmethod`."
    },
    {
        "id": 14,
        "question": "Коли виконується блок `else` у конструкції `try ... except ... else ... finally`?",
        "options": [
            "Тільки якщо в блоці `try` не виникло жодного винятку",
            "Завжди, незалежно від наявності помилок",
            "Тільки якщо спрацював блок `except`",
            "Коли блок `finally` повернув значення True"
        ],
        "correct_answer": "Тільки якщо в блоці `try` не виникло жодного винятку",
        "explanation": "Блок `else` виконується виключно тоді, коли код у блоці `try` завершився успішно без виникнення жодних винятків."
    },
    {
        "id": 15,
        "question": "Що таке GIL (Global Interpreter Lock) у CPython?",
        "options": [
            "М'ютекс, який дозволяє лише одному потоку виконувати байт-код Python одночасно в рамках одного процесу",
            "Вбудований фаєрвол для захисту мережевих сокетів інтерпретатора",
            "Змінна середовища, яка блокує доступ до пам'яті іншим додаткам",
            "Компілятор байт-коду у машинний код під час запуску"
        ],
        "correct_answer": "М'ютекс, який дозволяє лише одному потоку виконувати байт-код Python одночасно в рамках одного процесу",
        "explanation": "GIL у CPython синхронізує виконання потоків так, що одночасно виконується лише один нативний потік Python, що спрощує керування пам'яттю (reference counting)."
    },
    {
        "id": 16,
        "question": "Який клас зі стандартного модуля `collections` повертає значення за замовчуванням, якщо запитаного ключа немає в словнику?",
        "options": [
            "defaultdict",
            "OrderedDict",
            "Counter",
            "ChainMap"
        ],
        "correct_answer": "defaultdict",
        "explanation": "`collections.defaultdict` приймає фабрику значень за замовчуванням (наприклад, int, list) та викликає її при спробі звернення до відсутнього ключа."
    },
    {
        "id": 17,
        "question": "Що робить декоратор `@property` над методом класу?",
        "options": [
            "Дозволяє звертатися до методу як до атрибута (без дужок) та реалізовувати геттери/сеттери",
            "Робить метод статичним та забороняє його перевизначення в нащадках",
            "Автоматично кешує результати виклику функції на основі параметрів",
            "Приховує метод з результатів функції dir()"
        ],
        "correct_answer": "Дозволяє звертатися до методу як до атрибута (без дужок) та реалізовувати геттери/сеттери",
        "explanation": "`@property` перетворює метод на керований атрибут (дескриптор), надаючи можливість читання, запису (`@name.setter`) та видалення через синтаксис звичайного атрибута."
    },
    {
        "id": 18,
        "question": "Що таке Duck Typing ('качина типізація') в контексті Python?",
        "options": [
            "Концепція, коли важливий набір методів і властивостей об'єкта, а не його явна приналежність до конкретного класу",
            "Автоматичне приведення типів рядків до чисел у математичних операціях",
            "Обов'язкове наслідування від спеціального базового класу Duck",
            "Механізм перевірки типів за допомогою статичного аналізатора mypy"
        ],
        "correct_answer": "Концепція, коли важливий набір методів і властивостей об'єкта, а не його явна приналежність до конкретного класу",
        "explanation": "При качиній типізації діє принцип: 'якщо щось плаває як качка і крякає як качка, то це качка'. Інтерпретатор перевіряє наявність потрібної поведінки під час виконання."
    },
    {
        "id": 19,
        "question": "Що поверне вираз: `isinstance(True, int)`?",
        "options": [
            "True",
            "False",
            "TypeError",
            "None"
        ],
        "correct_answer": "True",
        "explanation": "У Python тип `bool` є підкласом типу `int` (`issubclass(bool, int) == True`), де `True` по суті є 1, а `False` — 0."
    },
    {
        "id": 20,
        "question": "Який декоратор зі стандартної бібліотеки `functools` реалізує автоматичне кешування результатів функції за принципом LRU?",
        "options": [
            "lru_cache",
            "cache_results",
            "memoize",
            "fast_cache"
        ],
        "correct_answer": "lru_cache",
        "explanation": "`@functools.lru_cache` кешує результати виклику функції з обмеженням розміру за алгоритмом Least Recently Used (найменш недавно використані)."
    }
]
```

---

### 3.3. `states/quiz_state.py` — FSM стани
```python
"""Модуль станів FSM для керування сесією проходження тесту.
"""

from aiogram.fsm.state import State, StatesGroup


class QuizStates(StatesGroup):
    """Стани користувача під час складання тесту."""
    answering = State()  # Користувач перебуває в процесі відповідей на питання
```

---

### 3.4. `keyboards/quiz_kb.py` — Генератор інлайн-клавіатур
```python
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
```

---

### 3.5. `handlers/quiz.py` — Логіка обробки запитів, часу та звіту
```python
"""Модуль обробників (хендлерів) для Telegram-бота тестування.

Реалізує:
- Старт тестування через команду /start
- Рандомізацію 10 питань та 4 варіантів відповідей
- Миттєву перевірку відповіді з поясненням
- Фіксацію часу початку, завершення та дати тестування
- Формування детального фінального звіту з результатами
"""

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
    """Повертає поточний час (за Києвом або системний локальний)."""
    try:
        return datetime.now(ZoneInfo("Europe/Kyiv"))
    except Exception:
        return datetime.now()


def prepare_quiz_session() -> List[Dict[str, Any]]:
    """Обирає 10 випадкових питань та перемішує варіанти відповідей для кожного.

    Returns:
        Список підготовлених запитань з перемішаними варіантами.
    """
    total_to_take = min(10, len(QUESTIONS_POOL))
    chosen_raw = random.sample(QUESTIONS_POOL, total_to_take)

    prepared: List[Dict[str, Any]] = []
    for item in chosen_raw:
        # Створюємо копію варіантів та перемішуємо їх
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
    """Надсилає поточне питання користувачу."""
    data = await state.get_data()
    q_index: int = data.get("current_index", 0)
    questions: List[Dict[str, Any]] = data.get("questions", [])

    if q_index >= len(questions):
        # Якщо питання вичерпано — завершуємо тест
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
    """Обробник команди /start. Ініціалізує нову сесію тестування."""
    await start_new_quiz(message, state)


@router.message(Command("help"))
async def handle_help(message: Message) -> None:
    """Обробник команди /help."""
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
    """Ініціалізує сесію та надсилає перше питання."""
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
    """Обробник вибору варіанта відповіді користувачем."""
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

    # Отримуємо вибраний індекс
    try:
        selected_idx = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Помилка обробки відповіді.")
        return

    current_q = questions[q_index]
    selected_option = current_q["options"][selected_idx]
    correct_option = current_q["correct_answer"]
    is_correct = (selected_option == correct_option)

    # Оновлення балів та історії
    score = data.get("score", 0) + (1 if is_correct else 0)
    history = data.get("history", [])
    history.append({
        "question": current_q["question"],
        "selected": selected_option,
        "correct": correct_option,
        "is_correct": is_correct,
    })

    # Формуємо зворотний зв'язок (feedback)
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

    # Прибираємо кнопки з попереднього повідомлення і показуємо результат
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    await callback.message.answer(feedback)

    # Переходимо до наступного запитання
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
    """Підраховує результати тестування, формує та надсилає фінальний звіт."""
    data = await state.get_data()
    score: int = data.get("score", 0)
    questions: List[Dict[str, Any]] = data.get("questions", [])
    total_q = len(questions) if questions else 10
    start_ts: float = data.get("start_timestamp", time.time())
    start_date_str: str = data.get("start_datetime_str", get_current_kyiv_time().strftime("%d.%m.%Y %H:%M:%S"))
    history: List[Dict[str, Any]] = data.get("history", [])

    # Розрахунок тривалості
    elapsed_seconds = max(1, int(time.time() - start_ts))
    minutes = elapsed_seconds // 60
    seconds = elapsed_seconds % 60
    if minutes > 0:
        duration_str = f"{minutes} хв {seconds} с"
    else:
        duration_str = f"{seconds} с"

    # Розрахунок відсотка успішності
    percentage = int((score / total_q) * 100) if total_q > 0 else 0

    # Визначення текстової оцінки / статусу
    if percentage >= 90:
        badge = "🏆 Відмінно! Глибоке розуміння Python та ООП!"
    elif percentage >= 70:
        badge = "👍 Добре! Солідний рівень знань."
    elif percentage >= 50:
        badge = "👌 Задовільно. Є над чим попрацювати."
    else:
        badge = "📚 Потрібно підтягнути теоретичний матеріал."

    # Деталізація відповідей
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
    """Обробник натискання кнопки 'Пройти тест ще раз'."""
    await callback.answer()
    await start_new_quiz(callback.message, state)
```

---

### 3.6. `main.py` — Точка входу та запуск Dispatcher
```python
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
```

---

### 3.7. Конфігураційні файли

**`requirements.txt`**:
```text
aiogram>=3.17.0,<4.0.0
python-dotenv>=1.0.1
```

**`Procfile`**:
```text
worker: python main.py
```

**`runtime.txt`**:
```text
python-3.11.9
```

---

## 4. Висновки

1. Під час виконання лабораторної роботи було детально вивчено асинхронні можливості створення Telegram-ботів за допомогою бібліотеки `aiogram 3.x`.
2. Застосовано концепцію скінченних автоматів (**FSM** — Finite State Machine) для ізольованого збереження прогресу кожного користувача окремо, що запобігає перетину сесій при паралельному проходженні тесту кількома людьми.
3. Реалізовано повноцінний алгоритм рандомізації як послідовності запитань (`random.sample`), так і варіантів відповідей (`random.shuffle`), що забезпечує унікальність кожного запуску тесту.
4. Розроблено механізм відліку реального часу тестування та фіксації таймстемпів, що дозволило сформувати інформативний підсумковий звіт із датою, тривалістю та оцінкою знань.
5. Забезпечено відповідність стандартам сучасного веброзгортання: підготовлено файли для розгортання бота у хмарних платформах Render та Heroku у режимі безперервного фонового процесу (`Background Worker`).
