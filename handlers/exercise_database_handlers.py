from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from utils.exercise_database import EXERCISE_DATABASE, get_exercises_by_muscle
import logging

router = Router()
logger = logging.getLogger(__name__)

# API для отримання фото вправ (безкоштовний)
EXERCISE_MEDIA_API = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"


def get_exercise_gif_url(exercise_name: str) -> str:
    """Генерує URL для GIF вправи"""
    # Конвертуємо назву у slug (приклад: "Жим лежа" -> "bench-press")
    # Для реального використання потрібна мапа назв
    slug = exercise_name.lower().replace(" ", "-").replace("'", "")
    return f"{EXERCISE_MEDIA_API}{slug}/images/0.gif"


def get_exercise_technique(exercise_name: str) -> str:
    """Повертає детальну техніку виконання вправи"""

    # База технік виконання
    techniques = {
        "Жим лежа со штангой": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Ляг на лавку, ноги міцно на підлозі
   • Штанга над грудьми, хват трохи ширше плечей
   • Лопатки зведені, груди "колесом"

2️⃣ **Опускання:**
   • Повільно опусти штангу до грудей (3-4 см нижче сосків)
   • Лікті під кутом ~45° до тулуба
   • Вдих при опусканні

3️⃣ **Підйом:**
   • Потужно видихни і вижми штангу вгору
   • Не відривай таз і ноги
   • Зафіксуй у верхній точці

⚠️ **Помилки:**
   ❌ Відбивання від грудей
   ❌ Відрив тазу від лавки
   ❌ Широкий хват (травмонебезпечно)
   ❌ Лікті надто розставлені

💡 **Порада:** Завжди працюй зі страхувальником!
""",

        "Присідання зі штангою": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Штанга на трапеціях (не на шиї!)
   • Ноги на ширині плечей, носки трохи врозлиз
   • Спина пряма, погляд вперед

2️⃣ **Присідання:**
   • Вдих, почни рух з відведення тазу назад
   • Присідай до паралелі стегон з підлогою
   • Коліна у напрямку носків
   • Спина пряма весь час

3️⃣ **Підйом:**
   • Потужний видих, вставай через п'яти
   • Розпрямляй ноги та тулуб одночасно
   • Не зводь коліна всередину

⚠️ **Помилки:**
   ❌ Округлення спини
   ❌ Коліна всередину
   ❌ Відрив п'ят від підлоги
   ❌ Надто швидкий темп

💡 **Порада:** Розминайся з порожньою штангою 2-3 підходи!
""",

        "Станова тяга": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Штанга над серединою стопи
   • Хват на ширині плечей або трохи ширше
   • Спина пряма, лопатки над грифом

2️⃣ **Підйом:**
   • Глибокий вдих, натягни пояс
   • Тягни штангу вгору близько до ніг
   • Спочатку розпрямляються ноги, потім корпус
   • Видих у верхній точці

3️⃣ **Опускання:**
   • Контрольоване опускання
   • Спина пряма весь час
   • Вдих при опусканні

⚠️ **Помилки:**
   ❌ Округлення спини (ДУЖЕ НЕБЕЗПЕЧНО!)
   ❌ Відрив штанги від ніг
   ❌ Ривки
   ❌ Розгинання тільки спиною

💡 **Порада:** Не роби станову в день ніг зі присідами!
""",

        "Підтягування": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Хват трохи ширше плечей
   • Повний вис, руки випрямлені
   • Лопатки зведені

2️⃣ **Підтягування:**
   • Потягни лікті вниз і назад
   • Підбородок вище перекладини
   • Груди до перекладини
   • Видих при підйомі

3️⃣ **Опускання:**
   • Повільно опустись у вихідне
   • Повний вис
   • Вдих при опусканні

⚠️ **Помилки:**
   ❌ Розгойдування
   ❌ Неповна амплітуда
   ❌ Ривки
   ❌ Підтягування шиєю, а не грудьми

💡 **Порада:** Не можеш підтягнутись? Використай резинку для допомоги!
""",

        "Тяга штанги в нахилі": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Нахил корпусу ~45°, спина пряма
   • Штанга в витягнутих руках
   • Ноги злегка зігнуті

2️⃣ **Тяга:**
   • Тягни штангу до низу живота
   • Лікті вздовж тулуба
   • Зводь лопатки у верхній точці
   • Видих при підйомі

3️⃣ **Опускання:**
   • Контрольоване розгинання рук
   • Вдих при опусканні
   • Спина залишається прямою

⚠️ **Помилки:**
   ❌ Округлення спини
   ❌ Ривки корпусом
   ❌ Тяга до грудей (не до живота)
   ❌ Занадто великий нахил

💡 **Порада:** Почни з малих ваг і відпрацюй техніку!
""",

        "Армійський жим": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Стій прямо, ноги на ширині плечей
   • Штанга на грудях, хват трохи ширше плечей
   • Лікті трохи вперед

2️⃣ **Жим вгору:**
   • Видихни і вижми штангу вгору
   • Голову трохи назад, щоб штанга пройшла
   • Випрями руки повністю вгорі
   • Штанга над серединою стопи

3️⃣ **Опускання:**
   • Контрольовано опусти на груди
   • Вдих при опусканні

⚠️ **Помилки:**
   ❌ Прогин у спині (небезпечно!)
   ❌ Жим перед собою (не над головою)
   ❌ Неповна амплітуда
   ❌ Розгойдування

💡 **Порада:** Втягни живіт і напружи ягодиці для стабільності!
""",

        "Жим ногами": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Сядь у тренажер, спина притиснута
   • Ноги на платформі на ширині плечей
   • Ступні паралельно

2️⃣ **Опускання:**
   • Зніми фіксатори
   • Опускай платформу до кута 90° у колінах
   • Коліна у напрямку носків
   • Вдих при опусканні

3️⃣ **Жим вгору:**
   • Потужно видихни і вижми платформу
   • Не розпрямляй коліна повністю
   • Контролюй рух

⚠️ **Помилки:**
   ❌ Відрив тазу від сидіння
   ❌ Коліна всередину
   ❌ Повне розпрямлення ніг
   ❌ Занадто низько (таз відривається)

💡 **Порада:** Ступні вище = більше навантаження на ягодиці!
""",

        "Підйом штанги на біцепс": """
🎯 **Техніка виконання:**

1️⃣ **Вихідне положення:**
   • Стій прямо, ноги на ширині плечей
   • Штанга в опущених руках
   • Лікті притиснуті до тулуба

2️⃣ **Підйом:**
   • Згинай руки в ліктях
   • Лікті нерухомі, працює тільки передпліччя
   • Видих при підйомі
   • Пікове скорочення вгорі

3️⃣ **Опускання:**
   • Повільно розгинай руки
   • Контролюй вагу
   • Вдих при опусканні

⚠️ **Помилки:**
   ❌ Розгойдування тулубом (читинг)
   ❌ Відведення ліктів вперед
   ❌ Швидке опускання
   ❌ Неповна амплітуда

💡 **Порада:** Якість > вага! Краще менше вага з ідеальною технікою!
"""
    }

    return techniques.get(exercise_name, """
🎯 **Техніка виконання:**

📝 Детальну техніку для цієї вправи ще не додано.

**Загальні принципи:**
• Повільне та контрольоване виконання
• Повна амплітуда руху
• Правильне дихання (видих на зусиллі)
• Розминка перед робочими підходами

💡 Порадься з тренером для правильної техніки!
""")


@router.message(F.text == "📚 База вправ")
async def show_exercise_database(message: Message):
    """Показує головне меню бази вправ"""

    # Групуємо вправи по м'язових групах
    muscle_groups = {}
    for exercise in EXERCISE_DATABASE:
        muscle = exercise.primary_muscle
        if muscle not in muscle_groups:
            muscle_groups[muscle] = []
        muscle_groups[muscle].append(exercise)

    from keyboards.main_keyboards import get_muscle_groups_keyboard

    text = (
        "📚 **База вправ**\n\n"
        f"🏋️ Всього вправ: {len(EXERCISE_DATABASE)}\n"
        f"💪 М'язових груп: {len(muscle_groups)}\n\n"
        "Обери м'язову групу для перегляду вправ:"
    )

    await message.answer(
        text,
        reply_markup=get_muscle_groups_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("muscle_"))
async def show_muscle_exercises(callback: CallbackQuery):
    """Показує вправи для вибраної м'язової групи"""
    muscle = callback.data.replace("muscle_", "")

    from keyboards.main_keyboards import get_exercises_by_muscle_keyboard

    exercises = [ex for ex in EXERCISE_DATABASE if muscle.lower() in ex.primary_muscle.lower()]

    if not exercises:
        await callback.answer("❌ Вправи не знайдено", show_alert=True)
        return

    await callback.answer()

    text = f"💪 **{muscle.upper()}**\n\n"
    text += f"📋 Знайдено вправ: {len(exercises)}\n\n"
    text += "Обери вправу для перегляду техніки:"

    await callback.message.edit_text(
        text,
        reply_markup=get_exercises_by_muscle_keyboard(muscle, exercises),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("exercise_detail_"))
async def show_exercise_detail(callback: CallbackQuery):
    """Показує детальну інформацію про вправу"""
    exercise_name = callback.data.replace("exercise_detail_", "")

    # Знаходимо вправу
    exercise = None
    for ex in EXERCISE_DATABASE:
        if ex.name == exercise_name:
            exercise = ex
            break

    if not exercise:
        await callback.answer("❌ Вправу не знайдено", show_alert=True)
        return

    await callback.answer("📖 Завантажую...", show_alert=False)

    # Формуємо детальний опис
    text = f"🏋️ **{exercise.name}**\n\n"
    text += f"🎯 **Основний м'яз:** {exercise.primary_muscle}\n"
    if exercise.secondary_muscles:
        text += f"💪 **Додаткові м'язи:** {exercise.secondary_muscles}\n"
    text += f"⚙️ **Обладнання:** {exercise.equipment}\n"
    text += f"📊 **Складність:** {exercise.difficulty}\n"
    text += f"📝 **Опис:** {exercise.description}\n\n"

    # Додаємо техніку виконання
    text += get_exercise_technique(exercise.name)

    from keyboards.main_keyboards import get_back_to_exercises_keyboard

    await callback.message.edit_text(
        text,
        reply_markup=get_back_to_exercises_keyboard(exercise.primary_muscle),
        parse_mode="Markdown"
    )


@router.callback_query(F.data == "back_to_muscle_groups")
async def back_to_muscle_groups(callback: CallbackQuery):
    """Повернутися до списку м'язових груп"""
    await callback.answer()

    muscle_groups = {}
    for exercise in EXERCISE_DATABASE:
        muscle = exercise.primary_muscle
        if muscle not in muscle_groups:
            muscle_groups[muscle] = []
        muscle_groups[muscle].append(exercise)

    from keyboards.main_keyboards import get_muscle_groups_keyboard

    text = (
        "📚 **База вправ**\n\n"
        f"🏋️ Всього вправ: {len(EXERCISE_DATABASE)}\n"
        f"💪 М'язових груп: {len(muscle_groups)}\n\n"
        "Обери м'язову групу для перегляду вправ:"
    )

    await callback.message.edit_text(
        text,
        reply_markup=get_muscle_groups_keyboard(),
        parse_mode="Markdown"
    )


@router.callback_query(F.data.startswith("back_to_muscle_"))
async def back_to_muscle_exercises(callback: CallbackQuery):
    """Повернутися до списку вправ м'язової групи"""
    muscle = callback.data.replace("back_to_muscle_", "")

    from keyboards.main_keyboards import get_exercises_by_muscle_keyboard

    exercises = [ex for ex in EXERCISE_DATABASE if muscle.lower() in ex.primary_muscle.lower()]

    await callback.answer()

    text = f"💪 **{muscle.upper()}**\n\n"
    text += f"📋 Знайдено вправ: {len(exercises)}\n\n"
    text += "Обери вправу для перегляду техніки:"

    await callback.message.edit_text(
        text,
        reply_markup=get_exercises_by_muscle_keyboard(muscle, exercises),
        parse_mode="Markdown"
    )
