from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from services.database_service import UserService, ProgramService
from keyboards.main_keyboards import (
    get_main_menu_keyboard,
    get_gender_keyboard,
    get_experience_keyboard,
    get_workouts_per_week_keyboard
)
from states import RegistrationStates
from utils.validators import InputValidator, ValidationError
from utils.error_handler import safe_handler, handle_db_errors, StructuredLogger
import logging

router = Router()
logger = StructuredLogger(__name__)


@router.message(CommandStart())
@safe_handler
async def cmd_start(message: Message, state: FSMContext):
    """Обробник команди /start"""
    async with async_session() as session:
        user = await UserService.get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username
        )

        logger.log_user_action(message.from_user.id, "start_command")

        # Перевіряємо чи заповнений профіль
        if not user.age or not user.workouts_per_week:
            await message.answer(
                "👋 Вітаю! Я твій персональний тренер.\n\n"
                "Щоб створити ідеальну програму тренувань, мені потрібно дізнатися трохи про тебе.\n\n"
                "📝 Давай заповнимо анкету!\n\n"
                "Скільки тобі років?\n\n"
                "💡 Введіть /cancel щоб скасувати",
                reply_markup=None
            )
            await state.set_state(RegistrationStates.age)
        else:
            await message.answer(
                f"З поверненням, {message.from_user.first_name}! 💪\n\n"
                "Обери дію з меню:",
                reply_markup=get_main_menu_keyboard()
            )


@router.message(RegistrationStates.age)
async def process_age(message: Message, state: FSMContext):
    """Обробка віку"""
    try:
        age = InputValidator.validate_age(message.text)
        await state.update_data(age=age)
        await message.answer(
            "📏 Який у тебе зріст? (у см, наприклад: 175)\n\n"
            "💡 Введіть /cancel щоб скасувати"
        )
        await state.set_state(RegistrationStates.height)
    except ValidationError as e:
        await message.answer(str(e))


@router.message(RegistrationStates.height)
async def process_height(message: Message, state: FSMContext):
    """Обробка зросту"""
    try:
        height = InputValidator.validate_height(message.text)
        await state.update_data(height=height)
        await message.answer(
            "⚖️ Яка твоя вага? (у кг, наприклад: 75)\n\n"
            "💡 Введіть /cancel щоб скасувати"
        )
        await state.set_state(RegistrationStates.weight)
    except ValidationError as e:
        await message.answer(str(e))


@router.message(RegistrationStates.weight)
async def process_weight(message: Message, state: FSMContext):
    """Обробка ваги"""
    try:
        weight = InputValidator.validate_body_weight(message.text)
        await state.update_data(weight=weight)
        await message.answer(
            "👤 Обери свою стать:",
            reply_markup=get_gender_keyboard()
        )
        await state.set_state(RegistrationStates.gender)
    except ValidationError as e:
        await message.answer(str(e))


@router.callback_query(RegistrationStates.gender, F.data.startswith("gender_"))
async def process_gender(callback: CallbackQuery, state: FSMContext):
    """Обробка статі"""
    gender = "чоловік" if callback.data == "gender_male" else "жінка"
    await state.update_data(gender=gender)

    await callback.answer("✅", show_alert=False)

    await callback.message.edit_text(
        f"✅ Стать: {gender}\n\n"
        "💪 Який у тебе тренувальний досвід?",
        reply_markup=get_experience_keyboard()
    )
    await state.set_state(RegistrationStates.experience)


@router.callback_query(RegistrationStates.experience, F.data.startswith("exp_"))
async def process_experience(callback: CallbackQuery, state: FSMContext):
    """Обробка досвіду"""
    exp_map = {
        "exp_beginner": "початківець",
        "exp_intermediate": "середній",
        "exp_advanced": "досвідчений"
    }
    experience = exp_map.get(callback.data, "середній")
    await state.update_data(experience=experience)

    await callback.answer("✅", show_alert=False)

    await callback.message.edit_text(
        f"✅ Досвід: {experience}\n\n"
        "📅 Скільки разів на тиждень ти готовий тренуватися?",
        reply_markup=get_workouts_per_week_keyboard()
    )
    await state.set_state(RegistrationStates.workouts_per_week)


@router.callback_query(RegistrationStates.workouts_per_week, F.data.startswith("wpw_"))
@safe_handler
async def process_workouts_per_week(callback: CallbackQuery, state: FSMContext):
    """Обробка кількості тренувань"""
    workouts_per_week = int(callback.data.split("_")[1])
    await state.update_data(workouts_per_week=workouts_per_week)

    await callback.answer("💾 Зберігаю профіль...", show_alert=False)

    # Зберігаємо дані в БД
    data = await state.get_data()

    async with async_session() as session:
        await UserService.update_user_profile(
            session,
            callback.from_user.id,
            age=data["age"],
            height=data["height"],
            weight=data["weight"],
            gender=data["gender"],
            experience=data["experience"],
            workouts_per_week=workouts_per_week
        )

        logger.log_user_action(
            callback.from_user.id,
            "profile_completed",
            {"workouts_per_week": workouts_per_week}
        )

        await callback.message.delete()
        await callback.message.answer(
            "✅ Профіль заповнено!\n\n"
            f"📊 Твої дані:\n"
            f"• Вік: {data['age']} років\n"
            f"• Зріст: {data['height']} см\n"
            f"• Вага: {data['weight']} кг\n"
            f"• Стать: {data['gender']}\n"
            f"• Досвід: {data['experience']}\n"
            f"• Тренувань на тиждень: {workouts_per_week}\n\n"
            "Тепер можеш створити свою першу програму! 🏋️",
            reply_markup=get_main_menu_keyboard()
        )
        await state.clear()


@router.callback_query(F.data == "cancel_registration")
async def cancel_registration(callback: CallbackQuery, state: FSMContext):
    """Скасування реєстрації"""
    await state.clear()
    await callback.message.edit_text(
        "❌ Реєстрацію скасовано.\n\n"
        "Для початку використай /start"
    )
    await callback.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Команда скасування"""
    current_state = await state.get_state()
    if current_state:
        await state.clear()
        await message.answer(
            "❌ Дію скасовано.\n\n"
            "Використай /start або обери дію з меню.",
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await message.answer(
            "Нічого скасовувати. Обери дію з меню:",
            reply_markup=get_main_menu_keyboard()
        )


@router.message(Command("menu"))
async def cmd_menu(message: Message):
    """Показати головне меню"""
    await message.answer(
        "📱 Головне меню:",
        reply_markup=get_main_menu_keyboard()
    )


@router.message(F.text == "📚 Довідка")
async def help_handler(message: Message):
    """Довідка"""
    help_text = """
📚 **Довідка по боту**

🏋 **Створити програму** - Створення тренувальної програми під твою мету

📋 **Моя програма** - Перегляд поточної програми тренувань

➕ **Записати тренування** - Логування виконаних вправ

📈 **Мій прогрес** - Перегляд прогресу та статистики

🔄 **Пересчитати програму** - Оновлення програми з урахуванням прогресу

⚙ **Налаштування** - Зміна профілю та налаштувань

**Прогресія:**
Коли ти досягаєш верхньої межі повторень у всіх підходах, бот автоматично рекомендує збільшити вагу на 2.5-5%.

**RIR (Reps in Reserve):**
1-2 RIR означає залишити 1-2 повторення до відмови.

**Делод:**
Кожні 6-10 тижнів необхідно робити делод (зниження навантаження) для відновлення.

Питання? Пиши /support
    """
    await message.answer(help_text, reply_markup=get_main_menu_keyboard())


@router.message(Command("menu"))
@safe_handler
async def cmd_menu(message: Message):
    """Показати головне меню"""
    await message.answer(
        "📱 **Головне меню**\n\nОбери дію:",
        reply_markup=get_main_menu_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "⚙ Налаштування")
async def settings_handler(message: Message):
    """Налаштування"""
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👤 Мій профіль", callback_data="settings_profile")],
            [InlineKeyboardButton(text="🔔 Нагадування", callback_data="settings_reminders")],
            [InlineKeyboardButton(text="🔄 Пересчитати програму", callback_data="settings_recalc")]
        ]
    )

    await message.answer(
        "⚙️ **Налаштування**\n\n"
        "Обери розділ:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    )


@router.callback_query(F.data == "settings_profile")
async def show_profile(callback: CallbackQuery):
    """Показати профіль"""
    async with async_session() as session:
        user = await UserService.get_user(session, callback.from_user.id)

        if user:
            settings_text = f"""
⚙️ **Твій профіль:**

• Вік: {user.age} років
• Зріст: {user.height} см
• Вага: {user.weight} кг
• Стать: {user.gender}
• Досвід: {user.experience}
• Тренувань на тиждень: {user.workouts_per_week}

Щоб змінити профіль, використай /start
            """
            await callback.message.edit_text(settings_text)
        else:
            await callback.message.edit_text("❌ Профіль не знайдено. Використай /start")

    await callback.answer()


@router.callback_query(F.data == "settings_reminders")
async def show_reminders(callback: CallbackQuery):
    """Показати налаштування нагадувань"""
    from services.reminder_service import ReminderService
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

    async with async_session() as session:
        reminders = await ReminderService.get_user_reminders(session, callback.from_user.id)

        if not reminders:
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="➕ Додати нагадування", callback_data="reminder_add")]
                ]
            )
            await callback.message.edit_text(
                "🔔 **Нагадування**\n\n"
                "У тебе немає активних нагадувань.\n"
                "Хочеш додати?",
                reply_markup=keyboard
            )
        else:
            text = "🔔 **Твої нагадування:**\n\n"
            buttons = []

            days_map = {
                "0": "Пн", "1": "Вт", "2": "Ср",
                "3": "Чт", "4": "Пт", "5": "Сб", "6": "Нд"
            }

            for reminder in reminders:
                days_str = ", ".join([days_map[d] for d in reminder.days_of_week.split(",")])
                status = "✅" if reminder.is_active else "❌"
                text += f"{status} {reminder.reminder_time} ({days_str})\n"

                buttons.append([
                    InlineKeyboardButton(
                        text=f"{'✅' if reminder.is_active else '❌'} {reminder.reminder_time}",
                        callback_data=f"reminder_toggle_{reminder.id}"
                    ),
                    InlineKeyboardButton(
                        text="🗑",
                        callback_data=f"reminder_delete_{reminder.id}"
                    )
                ])

            buttons.append([InlineKeyboardButton(text="➕ Додати", callback_data="reminder_add")])

            keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
            await callback.message.edit_text(text, reply_markup=keyboard)

    await callback.answer()


@router.callback_query(F.data == "settings_recalc")
async def recalc_from_settings(callback: CallbackQuery):
    """Пересчитати програму з налаштувань"""
    async with async_session() as session:
        from services.database_service import ProgramService
        from services.professional_program_generator import create_professional_program

        program = await ProgramService.get_active_program(session, callback.from_user.id)

        if not program:
            await callback.message.edit_text(
                "❌ У тебе немає активної програми.\n\n"
                "Створи програму: 🏋 Створити програму"
            )
            await callback.answer()
            return

        user = await UserService.get_user(session, callback.from_user.id)

        # Генеруємо нову програму з тією ж метою
        new_program_data = create_professional_program(
            goal_name=program.goal,
            workouts_per_week=user.workouts_per_week,
            experience=user.experience
        )

        if new_program_data:
            # Оновлюємо програму
            await ProgramService.create_program(
                session,
                user_id=callback.from_user.id,
                goal=program.goal,
                split_type=new_program_data["split_type"],
                workouts_per_week=new_program_data["workouts_per_week"],
                program_data=new_program_data
            )

            await callback.message.edit_text(
                "✅ Програма оновлена!\n\n"
                "Переглянути: 📋 Моя програма"
            )
        else:
            await callback.message.edit_text("❌ Помилка при оновленні програми")

    await callback.answer()
