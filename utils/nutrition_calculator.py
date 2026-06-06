"""Nutrition calculator with TDEE and macros"""
from typing import Dict, Tuple


class NutritionCalculator:
    """Калькулятор TDEE та макронутрієнтів"""

    # Activity multipliers
    ACTIVITY_LEVELS = {
        "sedentary": 1.2,        # Сидячий спосіб життя
        "light": 1.375,          # 1-2 тренування/тиждень
        "moderate": 1.55,        # 3-5 тренувань/тиждень
        "active": 1.725,         # 6-7 тренувань/тиждень
        "very_active": 1.9       # 2 тренування/день + фізична робота
    }

    # Goals caloric adjustment
    GOAL_ADJUSTMENTS = {
        "bulk": 1.15,            # +15% калорій для набору маси
        "cut": 0.85,             # -15% калорій для схуднення
        "maintain": 1.0,         # Підтримка ваги
        "lean_bulk": 1.10,       # +10% для чистого набору
        "aggressive_cut": 0.75   # -25% для агресивного схуднення
    }

    @staticmethod
    def calculate_bmr(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
        """
        Розрахунок BMR за формулою Mifflin-St Jeor (найточніша)

        Args:
            weight_kg: Вага в кг
            height_cm: Зріст в см
            age: Вік в роках
            gender: 'male' або 'female'

        Returns:
            BMR (калорій на день)
        """
        if gender.lower() == "male":
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161

        return round(bmr, 1)

    @staticmethod
    def calculate_tdee(bmr: float, activity_level: str) -> float:
        """
        Розрахунок TDEE (загальні витрати енергії)

        Args:
            bmr: Basal Metabolic Rate
            activity_level: Рівень активності (ключ з ACTIVITY_LEVELS)

        Returns:
            TDEE (калорій на день)
        """
        multiplier = NutritionCalculator.ACTIVITY_LEVELS.get(activity_level, 1.55)
        tdee = bmr * multiplier
        return round(tdee, 1)

    @staticmethod
    def calculate_target_calories(tdee: float, goal: str) -> float:
        """
        Розрахунок цільових калорій залежно від мети

        Args:
            tdee: Total Daily Energy Expenditure
            goal: Мета (ключ з GOAL_ADJUSTMENTS)

        Returns:
            Цільові калорії на день
        """
        adjustment = NutritionCalculator.GOAL_ADJUSTMENTS.get(goal, 1.0)
        target = tdee * adjustment
        return round(target, 1)

    @staticmethod
    def calculate_macros(target_calories: float, weight_kg: float, goal: str) -> Dict[str, float]:
        """
        Розрахунок макронутрієнтів (білки, жири, вуглеводи)

        Рекомендації:
        - Білок: 1.6-2.2 г/кг для гіпертрофії
        - Жири: 20-30% від калорій
        - Вуглеводи: решта калорій

        Args:
            target_calories: Цільові калорії
            weight_kg: Вага тіла в кг
            goal: Мета харчування

        Returns:
            Dict з protein, carbs, fats в грамах
        """
        # Білок залежно від мети
        if goal in ["bulk", "lean_bulk"]:
            protein_g_per_kg = 2.0
        elif goal in ["cut", "aggressive_cut"]:
            protein_g_per_kg = 2.2  # Більше білка при дефіциті
        else:
            protein_g_per_kg = 1.8

        protein_g = round(weight_kg * protein_g_per_kg, 1)

        # Жири: 25% від калорій (оптимально для гормонів)
        fat_calories = target_calories * 0.25
        fats_g = round(fat_calories / 9, 1)  # 9 ккал на грам

        # Білок та жири в калоріях
        protein_calories = protein_g * 4  # 4 ккал на грам
        remaining_calories = target_calories - protein_calories - fat_calories

        # Вуглеводи: решта калорій
        carbs_g = round(remaining_calories / 4, 1)  # 4 ккал на грам

        return {
            "protein": protein_g,
            "carbs": carbs_g,
            "fats": fats_g
        }

    @staticmethod
    def get_recommendations(goal: str, tdee: float, target_calories: float) -> str:
        """
        Отримати рекомендації по харчуванню залежно від мети

        Args:
            goal: Мета харчування
            tdee: TDEE користувача
            target_calories: Цільові калорії

        Returns:
            Текст з рекомендаціями
        """
        diff = target_calories - tdee

        recommendations = {
            "bulk": f"""
🍗 **Рекомендації для набору маси:**

📈 Профіцит калорій: +{abs(diff):.0f} ккал/день

**Основні принципи:**
• Їж 4-5 разів на день
• Білок: курка, яловичина, риба, яйця, творог
• Вуглеводи: гречка, рис, овсянка, макарони
• Здорові жири: горіхи, авокадо, олія
• Випивай 2-3л води на день

**Що уникати:**
❌ Надто великий профіцит (>500 ккал)
❌ Брудний набір (фастфуд)
❌ Пропускати прийоми їжі
""",
            "cut": f"""
🔥 **Рекомендації для схуднення:**

📉 Дефіцит калорій: {diff:.0f} ккал/день

**Основні принципи:**
• Їж 3-4 рази на день
• Високий білок для збереження м'язів
• Більше овочів для насичення
• Мінімум простих вуглеводів
• Випивай 2.5-3л води

**Що уникати:**
❌ Надто великий дефіцит (>500 ккал)
❌ Голодування
❌ Виключення жирів повністю
❌ Кардіо на порожній шлунок
""",
            "maintain": """
⚖️ **Рекомендації для підтримки:**

📊 Підтримка: калорії = TDEE

**Основні принципи:**
• Збалансоване харчування
• Регулярні прийоми їжі
• Різноманітність продуктів
• Контроль ваги 1 раз/тиждень

**Коригуй калорії якщо:**
• Вага змінюється >1кг за 2 тижні
• Змінюється кількість тренувань
"""
        }

        return recommendations.get(goal, "")

    @staticmethod
    def format_nutrition_plan(
        bmr: float,
        tdee: float,
        target_calories: float,
        macros: Dict[str, float],
        goal: str
    ) -> str:
        """
        Форматує повний план харчування

        Returns:
            Відформатований текст для Telegram
        """
        goal_emoji = {
            "bulk": "💪",
            "lean_bulk": "🏋️",
            "cut": "🔥",
            "aggressive_cut": "⚡",
            "maintain": "⚖️"
        }

        goal_names = {
            "bulk": "Набір маси",
            "lean_bulk": "Чистий набір",
            "cut": "Схуднення",
            "aggressive_cut": "Швидке схуднення",
            "maintain": "Підтримка ваги"
        }

        emoji = goal_emoji.get(goal, "🎯")
        goal_name = goal_names.get(goal, goal)

        text = f"{emoji} **ТВІЙ ПЛАН ХАРЧУВАННЯ**\n\n"
        text += f"🎯 **Мета:** {goal_name}\n\n"
        text += f"⚡ **BMR:** {bmr:.0f} ккал/день\n"
        text += f"🔥 **TDEE:** {tdee:.0f} ккал/день\n"
        text += f"🎯 **Цільові калорії:** {target_calories:.0f} ккал/день\n\n"

        text += "**МАКРОНУТРІЄНТИ:**\n"
        text += f"🥩 Білок: {macros['protein']:.0f}г ({macros['protein']*4:.0f} ккал)\n"
        text += f"🍚 Вуглеводи: {macros['carbs']:.0f}г ({macros['carbs']*4:.0f} ккал)\n"
        text += f"🥑 Жири: {macros['fats']:.0f}г ({macros['fats']*9:.0f} ккал)\n"

        return text
