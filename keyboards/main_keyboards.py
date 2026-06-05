from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import List


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Головне меню бота"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🏋 Створити програму"),
                KeyboardButton(text="📋 Моя програма")
            ],
            [
                KeyboardButton(text="➕ Записати тренування"),
                KeyboardButton(text="📈 Мій прогрес")
            ],
            [
                KeyboardButton(text="📊 Аналітика"),
                KeyboardButton(text="💡 Рекомендації")
            ],
            [
                KeyboardButton(text="📚 База вправ"),
                KeyboardButton(text="⏱ Таймер відпочинку")
            ],
            [
                KeyboardButton(text="⚙ Налаштування"),
                KeyboardButton(text="📚 Довідка")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_gender_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура вибору статі"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="👨 Чоловік", callback_data="gender_male"),
                InlineKeyboardButton(text="👩 Жінка", callback_data="gender_female")
            ]
        ]
    )
    return keyboard


def get_experience_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура вибору досвіду"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🌱 Початківець (0-6 місяців)", callback_data="exp_beginner")],
            [InlineKeyboardButton(text="💪 Середній (6-24 місяці)", callback_data="exp_intermediate")],
            [InlineKeyboardButton(text="🏆 Досвідчений (2+ роки)", callback_data="exp_advanced")]
        ]
    )
    return keyboard


def get_workouts_per_week_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура вибору кількості тренувань"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="3", callback_data="wpw_3"),
                InlineKeyboardButton(text="4", callback_data="wpw_4"),
                InlineKeyboardButton(text="5", callback_data="wpw_5"),
                InlineKeyboardButton(text="6", callback_data="wpw_6")
            ]
        ]
    )
    return keyboard


def get_goals_keyboard(page: int = 0, goals_per_page: int = 10) -> InlineKeyboardMarkup:
    """Клавіатура вибору цілі з пагінацією"""
    from utils.goals import get_all_goals

    all_goals = get_all_goals()
    total_pages = (len(all_goals) + goals_per_page - 1) // goals_per_page

    start_idx = page * goals_per_page
    end_idx = start_idx + goals_per_page
    page_goals = all_goals[start_idx:end_idx]

    buttons = []
    for goal in page_goals:
        buttons.append([InlineKeyboardButton(
            text=goal.name,
            callback_data=f"goal_{goal.name}"
        )])

    # Навігаційні кнопки
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"goals_page_{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton(text="Вперед ➡️", callback_data=f"goals_page_{page+1}"))

    if nav_buttons:
        buttons.append(nav_buttons)

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_confirm_program_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура підтвердження програми"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Підтвердити", callback_data="confirm_program_yes"),
                InlineKeyboardButton(text="❌ Скасувати", callback_data="confirm_program_no")
            ]
        ]
    )
    return keyboard


def get_workout_selection_keyboard(workouts: List[str]) -> InlineKeyboardMarkup:
    """Клавіатура вибору тренування"""
    buttons = []
    for i, workout in enumerate(workouts):
        buttons.append([InlineKeyboardButton(
            text=workout,
            callback_data=f"workout_{i}"
        )])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_exercise_selection_keyboard(exercises: List[dict]) -> InlineKeyboardMarkup:
    """Клавіатура вибору вправи"""
    buttons = []
    for i, exercise in enumerate(exercises):
        buttons.append([InlineKeyboardButton(
            text=f"{exercise['name']} ({exercise['sets']}x{exercise['reps']})",
            callback_data=f"exercise_{i}"
        )])

    buttons.append([InlineKeyboardButton(text="✅ Завершити тренування", callback_data="finish_workout")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура скасування"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="❌ Скасувати", callback_data="cancel")]
        ]
    )
    return keyboard


def get_muscle_groups_keyboard() -> InlineKeyboardMarkup:
    """Клавіатура вибору м'язової групи"""
    from utils.exercise_database import EXERCISE_DATABASE

    # Отримуємо унікальні м'язові групи
    muscle_groups = {}
    for exercise in EXERCISE_DATABASE:
        muscle = exercise.primary_muscle
        if muscle not in muscle_groups:
            muscle_groups[muscle] = 0
        muscle_groups[muscle] += 1

    # Емодзі для м'язових груп
    muscle_emojis = {
        "грудь": "💪",
        "спина": "🦾",
        "плечі": "🏋️",
        "біцепс": "💪",
        "трицепс": "💪",
        "ноги": "🦵",
        "пресс": "🔥",
    }

    buttons = []
    for muscle, count in sorted(muscle_groups.items()):
        emoji = muscle_emojis.get(muscle.lower(), "🏋️")
        buttons.append([InlineKeyboardButton(
            text=f"{emoji} {muscle.capitalize()} ({count})",
            callback_data=f"muscle_{muscle}"
        )])

    buttons.append([InlineKeyboardButton(text="🏠 Головне меню", callback_data="back_to_main")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_exercises_by_muscle_keyboard(muscle: str, exercises: List) -> InlineKeyboardMarkup:
    """Клавіатура зі списком вправ для м'язової групи"""
    buttons = []

    for exercise in exercises[:15]:  # Максимум 15 вправ на сторінку
        # Скорочуємо назву якщо дуже довга
        name = exercise.name[:35] + "..." if len(exercise.name) > 35 else exercise.name
        buttons.append([InlineKeyboardButton(
            text=f"🏋️ {name}",
            callback_data=f"exercise_detail_{exercise.name}"
        )])

    buttons.append([InlineKeyboardButton(text="⬅️ Назад до груп", callback_data="back_to_muscle_groups")])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_back_to_exercises_keyboard(muscle: str) -> InlineKeyboardMarkup:
    """Клавіатура повернення до списку вправ"""
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад до вправ", callback_data=f"back_to_muscle_{muscle}")]
        ]
    )
    return keyboard

