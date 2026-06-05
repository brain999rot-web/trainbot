"""Калькулятори для розрахунку силових показників"""
from typing import Dict, Tuple


class StrengthCalculator:
    """Калькулятор одноповторного максимуму (1RM) та тренувальних ваг"""

    @staticmethod
    def calculate_1rm_epley(weight: float, reps: int) -> float:
        """
        Формула Epley: 1RM = weight × (1 + reps/30)
        Найбільш популярна формула
        """
        if reps == 1:
            return weight
        return weight * (1 + reps / 30)

    @staticmethod
    def calculate_1rm_brzycki(weight: float, reps: int) -> float:
        """
        Формула Brzycki: 1RM = weight × (36 / (37 - reps))
        Точніша для діапазону 2-10 повторень
        """
        if reps == 1:
            return weight
        if reps >= 37:
            reps = 36  # Захист від ділення на нуль
        return weight * (36 / (37 - reps))

    @staticmethod
    def calculate_1rm_lombardi(weight: float, reps: int) -> float:
        """
        Формула Lombardi: 1RM = weight × reps^0.10
        Добре працює для малої кількості повторень
        """
        if reps == 1:
            return weight
        return weight * (reps ** 0.10)

    @staticmethod
    def calculate_1rm_mayhew(weight: float, reps: int) -> float:
        """
        Формула Mayhew: 1RM = (100 × weight) / (52.2 + 41.9 × e^(-0.055 × reps))
        """
        if reps == 1:
            return weight
        import math
        return (100 * weight) / (52.2 + 41.9 * math.exp(-0.055 * reps))

    @staticmethod
    def calculate_1rm_wathen(weight: float, reps: int) -> float:
        """
        Формула Wathen: 1RM = (100 × weight) / (48.8 + 53.8 × e^(-0.075 × reps))
        """
        if reps == 1:
            return weight
        import math
        return (100 * weight) / (48.8 + 53.8 * math.exp(-0.075 * reps))

    @staticmethod
    def calculate_average_1rm(weight: float, reps: int) -> Dict[str, float]:
        """
        Розраховує 1RM за всіма формулами та повертає середнє значення

        Returns:
            dict з результатами кожної формули + середнє
        """
        if reps > 12:
            # Для більше 12 повторень формули неточні
            reps = 12

        results = {
            'epley': StrengthCalculator.calculate_1rm_epley(weight, reps),
            'brzycki': StrengthCalculator.calculate_1rm_brzycki(weight, reps),
            'lombardi': StrengthCalculator.calculate_1rm_lombardi(weight, reps),
            'mayhew': StrengthCalculator.calculate_1rm_mayhew(weight, reps),
            'wathen': StrengthCalculator.calculate_1rm_wathen(weight, reps)
        }

        # Середнє значення
        avg = sum(results.values()) / len(results)
        results['average'] = avg

        return results

    @staticmethod
    def calculate_training_weights(one_rm: float) -> Dict[int, float]:
        """
        Розраховує тренувальні ваги від 1RM

        Args:
            one_rm: Одноповторний максимум

        Returns:
            Словник з відсотками та вагами
        """
        percentages = [50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100]

        training_weights = {}
        for percent in percentages:
            training_weights[percent] = round(one_rm * (percent / 100), 1)

        return training_weights

    @staticmethod
    def get_rep_ranges_for_weight(one_rm: float) -> Dict[str, Tuple[float, str]]:
        """
        Повертає рекомендовані діапазони повторень для різних цілей

        Returns:
            dict: {goal: (weight, rep_range)}
        """
        recommendations = {
            'Сила (1-5 повт.)': (one_rm * 0.85, '85-100% від 1RM'),
            'Гіпертрофія (6-12 повт.)': (one_rm * 0.70, '67-85% від 1RM'),
            'Витривалість (12-20 повт.)': (one_rm * 0.60, '50-67% від 1RM'),
            'Технічна робота': (one_rm * 0.50, '40-60% від 1RM')
        }

        return {
            goal: (round(weight, 1), range_desc)
            for goal, (weight, range_desc) in recommendations.items()
        }

    @staticmethod
    def format_1rm_results(
        exercise_name: str,
        weight: float,
        reps: int,
        results: Dict[str, float]
    ) -> str:
        """Форматує результати розрахунку 1RM"""

        message = f"🏋️ **{exercise_name}**\n\n"
        message += f"Ви виконали: **{weight}кг × {reps} повт.**\n\n"
        message += "📊 **Розрахунковий 1RM:**\n\n"

        # Показуємо результати різних формул
        message += f"• Epley: {results['epley']:.1f}кг\n"
        message += f"• Brzycki: {results['brzycki']:.1f}кг\n"
        message += f"• Lombardi: {results['lombardi']:.1f}кг\n"
        message += f"• Mayhew: {results['mayhew']:.1f}кг\n"
        message += f"• Wathen: {results['wathen']:.1f}кг\n\n"

        message += f"🎯 **Середній 1RM: {results['average']:.1f}кг**\n"

        return message

    @staticmethod
    def format_training_weights(one_rm: float) -> str:
        """Форматує тренувальні ваги"""
        weights = StrengthCalculator.calculate_training_weights(one_rm)

        message = "💪 **Тренувальні ваги:**\n\n"

        for percent, weight in weights.items():
            if percent == 100:
                message += f"**{percent}% (1RM) = {weight}кг**\n"
            else:
                message += f"{percent}% = {weight}кг\n"

        return message

    @staticmethod
    def format_rep_recommendations(one_rm: float) -> str:
        """Форматує рекомендації по діапазонах повторень"""
        recommendations = StrengthCalculator.get_rep_ranges_for_weight(one_rm)

        message = "🎯 **Рекомендації по тренуванням:**\n\n"

        for goal, (weight, range_desc) in recommendations.items():
            message += f"**{goal}**\n"
            message += f"Вага: ~{weight}кг ({range_desc})\n\n"

        return message
