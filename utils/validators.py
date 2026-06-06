"""Validators for user input data"""
import re
from typing import Tuple, Optional


class ValidationError(Exception):
    """Custom validation error"""
    pass


class InputValidator:
    """Validates user input across the bot"""

    # Regex patterns
    WEIGHT_REPS_PATTERN = re.compile(r'^(\d+(?:\.\d+)?)\s+(\d+)$')
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_а-яА-ЯіІїЇєЄ\s]{2,50}$')

    # Value ranges
    MIN_WEIGHT_KG = 0.5
    MAX_WEIGHT_KG = 500.0
    MIN_REPS = 1
    MAX_REPS = 100
    MIN_AGE = 10
    MAX_AGE = 100
    MIN_HEIGHT_CM = 100
    MAX_HEIGHT_CM = 250
    MIN_BODY_WEIGHT_KG = 30.0
    MAX_BODY_WEIGHT_KG = 300.0
    MIN_WORKOUTS_PER_WEEK = 2
    MAX_WORKOUTS_PER_WEEK = 6
    MIN_CALORIES = 500
    MAX_CALORIES = 10000

    @classmethod
    def validate_weight_reps(cls, input_str: str) -> Tuple[float, int]:
        """
        Validates and parses weight and reps input.

        Args:
            input_str: String in format "weight reps" (e.g., "50 10" or "50.5 12")

        Returns:
            Tuple of (weight, reps)

        Raises:
            ValidationError: If format is invalid or values out of range
        """
        input_str = input_str.strip()

        match = cls.WEIGHT_REPS_PATTERN.match(input_str)
        if not match:
            raise ValidationError(
                "❌ Неправильний формат!\n\n"
                "Використовуйте: <вага> <повторення>\n"
                "Приклади:\n"
                "  • 50 10\n"
                "  • 22.5 12\n"
                "  • 100 8"
            )

        weight = float(match.group(1))
        reps = int(match.group(2))

        if not (cls.MIN_WEIGHT_KG <= weight <= cls.MAX_WEIGHT_KG):
            raise ValidationError(
                f"❌ Вага повинна бути від {cls.MIN_WEIGHT_KG} до {cls.MAX_WEIGHT_KG} кг"
            )

        if not (cls.MIN_REPS <= reps <= cls.MAX_REPS):
            raise ValidationError(
                f"❌ Кількість повторень повинна бути від {cls.MIN_REPS} до {cls.MAX_REPS}"
            )

        return weight, reps

    @classmethod
    def validate_age(cls, age: int) -> int:
        """
        Validates age input.

        Args:
            age: User's age

        Returns:
            Validated age

        Raises:
            ValidationError: If age is out of range
        """
        try:
            age = int(age)
        except (ValueError, TypeError):
            raise ValidationError("❌ Вік повинен бути числом")

        if not (cls.MIN_AGE <= age <= cls.MAX_AGE):
            raise ValidationError(
                f"❌ Вік повинен бути від {cls.MIN_AGE} до {cls.MAX_AGE} років"
            )

        return age

    @classmethod
    def validate_height(cls, height: float) -> float:
        """
        Validates height input.

        Args:
            height: User's height in cm

        Returns:
            Validated height

        Raises:
            ValidationError: If height is out of range
        """
        try:
            height = float(height)
        except (ValueError, TypeError):
            raise ValidationError("❌ Зріст повинен бути числом")

        if not (cls.MIN_HEIGHT_CM <= height <= cls.MAX_HEIGHT_CM):
            raise ValidationError(
                f"❌ Зріст повинен бути від {cls.MIN_HEIGHT_CM} до {cls.MAX_HEIGHT_CM} см"
            )

        return height

    @classmethod
    def validate_body_weight(cls, weight: float) -> float:
        """
        Validates body weight input.

        Args:
            weight: User's body weight in kg

        Returns:
            Validated weight

        Raises:
            ValidationError: If weight is out of range
        """
        try:
            weight = float(weight)
        except (ValueError, TypeError):
            raise ValidationError("❌ Вага повинна бути числом")

        if not (cls.MIN_BODY_WEIGHT_KG <= weight <= cls.MAX_BODY_WEIGHT_KG):
            raise ValidationError(
                f"❌ Вага повинна бути від {cls.MIN_BODY_WEIGHT_KG} до {cls.MAX_BODY_WEIGHT_KG} кг"
            )

        return weight

    @classmethod
    def validate_workouts_per_week(cls, workouts: int) -> int:
        """
        Validates workouts per week input.

        Args:
            workouts: Number of workouts per week

        Returns:
            Validated workouts count

        Raises:
            ValidationError: If count is out of range
        """
        try:
            workouts = int(workouts)
        except (ValueError, TypeError):
            raise ValidationError("❌ Кількість тренувань повинна бути числом")

        if not (cls.MIN_WORKOUTS_PER_WEEK <= workouts <= cls.MAX_WORKOUTS_PER_WEEK):
            raise ValidationError(
                f"❌ Кількість тренувань повинна бути від {cls.MIN_WORKOUTS_PER_WEEK} до {cls.MAX_WORKOUTS_PER_WEEK} на тиждень"
            )

        return workouts

    @classmethod
    def validate_gender(cls, gender: str) -> str:
        """
        Validates gender input.

        Args:
            gender: User's gender

        Returns:
            Validated gender

        Raises:
            ValidationError: If gender is invalid
        """
        gender = gender.strip().lower()
        valid_genders = ['чоловік', 'жінка', 'male', 'female', 'м', 'ж', 'm', 'f']

        if gender not in valid_genders:
            raise ValidationError(
                "❌ Оберіть стать: Чоловік або Жінка"
            )

        # Normalize to Ukrainian
        if gender in ['male', 'm', 'м', 'чоловік']:
            return 'Чоловік'
        else:
            return 'Жінка'

    @classmethod
    def validate_experience(cls, experience: str) -> str:
        """
        Validates experience level input.

        Args:
            experience: User's training experience

        Returns:
            Validated experience

        Raises:
            ValidationError: If experience is invalid
        """
        experience = experience.strip().lower()
        valid_levels = {
            'новачок': 'Новачок',
            'початківець': 'Новачок',
            'середній': 'Середній',
            'просунутий': 'Просунутий',
            'beginner': 'Новачок',
            'intermediate': 'Середній',
            'advanced': 'Просунутий'
        }

        if experience not in valid_levels:
            raise ValidationError(
                "❌ Оберіть рівень досвіду:\n"
                "• Новачок\n"
                "• Середній\n"
                "• Просунутий"
            )

        return valid_levels[experience]

    @classmethod
    def sanitize_string(cls, text: str, max_length: int = 255) -> str:
        """
        Sanitizes string input to prevent SQL injection and XSS.

        Args:
            text: Input text
            max_length: Maximum allowed length

        Returns:
            Sanitized string
        """
        if not text:
            return ""

        # Remove leading/trailing whitespace
        text = text.strip()

        # Truncate to max length
        text = text[:max_length]

        # Remove potentially dangerous characters
        # SQLAlchemy handles parameterized queries, but extra safety
        dangerous_chars = ['<', '>', '"', "'", '`', ';', '\\', '\x00']
        for char in dangerous_chars:
            text = text.replace(char, '')

        return text

    @classmethod
    def validate_set_number(cls, set_num: int, max_sets: int = 10) -> int:
        """
        Validates set number input.

        Args:
            set_num: Set number
            max_sets: Maximum allowed sets

        Returns:
            Validated set number

        Raises:
            ValidationError: If set number is invalid
        """
        try:
            set_num = int(set_num)
        except (ValueError, TypeError):
            raise ValidationError("❌ Номер підходу повинен бути числом")

        if not (1 <= set_num <= max_sets):
            raise ValidationError(
                f"❌ Номер підходу повинен бути від 1 до {max_sets}"
            )

        return set_num


def format_validation_help() -> str:
    """Returns formatted help text for input validation"""
    return (
        "📝 <b>Формати введення:</b>\n\n"
        "🏋️ <b>Вага та повторення:</b>\n"
        "  • Формат: <code>вага повторення</code>\n"
        "  • Приклад: <code>50 10</code> або <code>22.5 12</code>\n\n"
        "📊 <b>Діапазони значень:</b>\n"
        f"  • Вага вправи: {InputValidator.MIN_WEIGHT_KG}-{InputValidator.MAX_WEIGHT_KG} кг\n"
        f"  • Повторення: {InputValidator.MIN_REPS}-{InputValidator.MAX_REPS}\n"
        f"  • Вік: {InputValidator.MIN_AGE}-{InputValidator.MAX_AGE} років\n"
        f"  • Зріст: {InputValidator.MIN_HEIGHT_CM}-{InputValidator.MAX_HEIGHT_CM} см\n"
        f"  • Вага тіла: {InputValidator.MIN_BODY_WEIGHT_KG}-{InputValidator.MAX_BODY_WEIGHT_KG} кг\n"
        f"  • Тренувань/тиждень: {InputValidator.MIN_WORKOUTS_PER_WEEK}-{InputValidator.MAX_WORKOUTS_PER_WEEK}"
    )
