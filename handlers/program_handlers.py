from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from database import async_session
from services.database_service import UserService, ProgramService
from services.professional_program_generator import create_professional_program
from keyboards.main_keyboards import (
    get_goals_keyboard,
    get_confirm_program_keyboard
)
from states import ProgramCreationStates
import logging

router = Router()
logger = logging.getLogger(__name__)


@router.message(F.text == "🏋 Створити програму")
async def create_program_start(message: Message, state: FSMContext):
    """Початок створення програми"""
    async with async_session() as session:
        user = await UserService.get_user(session, message.from_user.id)

        if not user or not user.workouts_per_week:
            await message.answer(
                "❌ Спочатку заповни профіль!\nВикористай команду /start"
            )
            return

        await message.answer(
            "🎯 Обери свою тренувальну мету:\n\n"
            "Це визначить структуру твоєї програми, обсяг тренувань та акценти.",
            reply_markup=get_goals_keyboard(page=0)
        )
        await state.set_state(ProgramCreationStates.choose_goal)


@router.callback_query(F.data.startswith("goals_page_"))
async def goals_pagination(callback: CallbackQuery, state: FSMContext):
    """Пагінація цілей"""
    page = int(callback.data.split("_")[2])
    await callback.answer("🔄 Завантажую...", show_alert=False)
    await callback.message.edit_reply_markup(
        reply_markup=get_goals_keyboard(page=page)
    )


@router.callback_query(ProgramCreationStates.choose_goal, F.data.startswith("goal_"))
async def process_goal_selection(callback: CallbackQuery, state: FSMContext):
    """Обробка вибору мети"""
    goal_name = callback.data.replace("goal_", "")

    await callback.answer("⏳ Генерую програму...", show_alert=False)

    async with async_session() as session:
        user = await UserService.get_user(session, callback.from_user.id)

        if not user:
            await callback.message.answer("❌ Користувача не знайдено")
            await callback.answer()
            return

        # Генеруємо програму
        program_data = create_professional_program(
            goal_name=goal_name,
            workouts_per_week=user.workouts_per_week,
            experience=user.experience
        )

        if not program_data:
            await callback.message.answer("❌ Помилка при створенні програми")
            await callback.answer()
            return

        # Зберігаємо у стані
        await state.update_data(
            goal_name=goal_name,
            program_data=program_data
        )

        # Формуємо опис програми
        program_description = _format_program_description(program_data)

        await callback.message.edit_text(
            f"📋 **Твоя програма:**\n\n{program_description}\n\n"
            "Підтверджуєш програму?",
            reply_markup=get_confirm_program_keyboard(),
            parse_mode="Markdown"
        )
        await state.set_state(ProgramCreationStates.confirm_program)


@router.callback_query(ProgramCreationStates.confirm_program, F.data == "confirm_program_yes")
async def confirm_program(callback: CallbackQuery, state: FSMContext):
    """Підтвердження програми"""
    await callback.answer("💾 Зберігаю програму...", show_alert=False)

    data = await state.get_data()
    program_data = data.get("program_data")
    goal_name = data.get("goal_name")

    async with async_session() as session:
        try:
            # Зберігаємо програму в БД
            program = await ProgramService.create_program(
                session,
                user_id=callback.from_user.id,
                goal=goal_name,
                split_type=program_data["split_type"],
                workouts_per_week=program_data["workouts_per_week"],
                program_data=program_data
            )

            await callback.message.edit_text(
                "✅ **Програма створена!**\n\n"
                "Тепер ти можеш:\n"
                "• Переглянути програму: 📋 Моя програма\n"
                "• Почати тренування: ➕ Записати тренування\n\n"
                "Успішних тренувань! 💪",
                parse_mode="Markdown"
            )
            await state.clear()
        except Exception as e:
            logger.error(f"Помилка при створенні програми: {e}")
            await callback.message.edit_text(
                "❌ **Помилка при збереженні програми**\n\n"
                "Спробуй ще раз: 🏋 Створити програму",
                parse_mode="Markdown"
            )
            await state.clear()


@router.callback_query(ProgramCreationStates.confirm_program, F.data == "confirm_program_no")
async def cancel_program(callback: CallbackQuery, state: FSMContext):
    """Скасування програми"""
    await callback.answer("❌ Скасовано", show_alert=False)
    await callback.message.edit_text(
        "❌ Створення програми скасовано.\n\n"
        "Можеш створити нову програму в будь-який час!"
    )
    await state.clear()


@router.message(F.text == "📋 Моя програма")
async def view_program(message: Message):
    """Перегляд поточної програми"""
    async with async_session() as session:
        program = await ProgramService.get_active_program(session, message.from_user.id)

        if not program:
            await message.answer(
                "❌ У тебе ще немає активної програми.\n\n"
                "Створи програму: 🏋 Створити програму"
            )
            return

        program_text = _format_full_program(program.program_data)
        await message.answer(program_text)


@router.message(F.text == "🔄 Пересчитати програму")
async def recalculate_program(message: Message):
    """Пересчитати програму"""
    async with async_session() as session:
        program = await ProgramService.get_active_program(session, message.from_user.id)

        if not program:
            await message.answer(
                "❌ У тебе немає активної програми.\n\n"
                "Створи програму: 🏋 Створити програму"
            )
            return

        user = await UserService.get_user(session, message.from_user.id)

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
                user_id=message.from_user.id,
                goal=program.goal,
                split_type=new_program_data["split_type"],
                workouts_per_week=new_program_data["workouts_per_week"],
                program_data=new_program_data
            )

            await message.answer(
                "✅ Програма оновлена!\n\n"
                "Переглянути: 📋 Моя програма"
            )
        else:
            await message.answer("❌ Помилка при оновленні програми")


def _format_program_description(program_data: dict) -> str:
    """Форматує короткий опис програми"""
    text = f"**Мета:** {program_data['goal']}\n"
    text += f"**Сплит:** {program_data['split_type']}\n"
    text += f"**Тренувань на тиждень:** {program_data['workouts_per_week']}\n\n"

    text += "**Тренування:**\n"
    for workout in program_data['workouts']:
        text += f"• {workout['name']} ({len(workout['exercises'])} вправ)\n"

    return text


def _format_full_program(program_data: dict) -> str:
    """Форматує повний опис програми"""
    text = f"📋 **Твоя програма тренувань**\n\n"
    text += f"🎯 Мета: {program_data['goal']}\n"
    text += f"📊 Сплит: {program_data['split_type']}\n"
    text += f"📅 Тренувань: {program_data['workouts_per_week']}/тиждень\n\n"

    for i, workout in enumerate(program_data['workouts'], 1):
        text += f"**{i}. {workout['name']}**\n"
        for j, exercise in enumerate(workout['exercises'], 1):
            text += f"  {j}. {exercise['name']}\n"
            text += f"     • {exercise['sets']} x {exercise['reps']} повторень\n"
            text += f"     • RIR: {exercise['rir']}\n"
            if exercise.get('notes'):
                text += f"     • {exercise['notes']}\n"
        text += "\n"

    text += f"ℹ️ {program_data['notes']}\n"

    return text
