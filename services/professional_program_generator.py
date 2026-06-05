"""Професійний генератор тренувальних програм з науковим підходом"""
from typing import Dict, List, Tuple, Set
from utils.goals import Goal, get_goal_by_name
from utils.exercise_database import get_exercises_by_muscle, ExerciseData
import random


class ProfessionalProgramGenerator:
    """Генератор програм з правильним обсягом та структурою"""

    # Мінімальні та максимальні підходи на м'яз на тиждень
    VOLUME_GUIDELINES = {
        "beginner": {"min": 10, "max": 15},
        "intermediate": {"min": 12, "max": 20},
        "advanced": {"min": 15, "max": 26}
    }

    def __init__(self, goal: Goal, workouts_per_week: int, experience: str):
        self.goal = goal
        self.workouts_per_week = workouts_per_week
        self.experience = self._normalize_experience(experience)
        self.used_exercises: Set[str] = set()

    def _normalize_experience(self, exp: str) -> str:
        """Нормалізує рівень досвіду"""
        exp_lower = exp.lower()
        if "початк" in exp_lower or "новач" in exp_lower or "beginner" in exp_lower:
            return "beginner"
        elif "досвід" in exp_lower or "серед" in exp_lower or "intermediate" in exp_lower:
            return "intermediate"
        else:
            return "advanced"

    def generate_program(self) -> Dict:
        """Генерує професійну програму"""
        split_type = self._determine_optimal_split()
        workouts = self._create_optimal_workouts(split_type)

        return {
            "goal": self.goal.name,
            "split_type": split_type,
            "workouts_per_week": self.workouts_per_week,
            "workouts": workouts,
            "notes": self._generate_professional_notes()
        }

    def _determine_optimal_split(self) -> str:
        """Визначає оптимальний сплит на основі частоти"""
        if self.workouts_per_week == 3:
            return "Full Body"
        elif self.workouts_per_week == 4:
            return "Upper Lower"
        elif self.workouts_per_week == 5:
            # Перевіряємо пріоритети
            if self._has_arm_priority():
                return "Upper Lower Arms"
            return "Push Pull Legs"
        else:  # 6
            return "Push Pull Legs"

    def _has_arm_priority(self) -> bool:
        """Перевіряє чи руки в пріоритеті"""
        arm_priority = 0
        for muscle in ["біцепс", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                priority = self.goal.muscle_priorities[muscle].priority
                if priority == "high":
                    arm_priority += 1
        return arm_priority >= 2

    def _create_optimal_workouts(self, split_type: str) -> List[Dict]:
        """Створює оптимальні тренування"""
        if split_type == "Full Body":
            return self._create_full_body_3x()
        elif split_type == "Upper Lower":
            return self._create_upper_lower_4x()
        elif split_type == "Upper Lower Arms":
            return self._create_upper_lower_arms_5x()
        elif split_type == "Push Pull Legs":
            if self.workouts_per_week == 5:
                return self._create_ppl_5x()
            else:
                return self._create_ppl_6x()
        return []

    def _create_full_body_3x(self) -> List[Dict]:
        """Full Body 3x тиждень - 7-8 вправ на тренування"""
        workouts = []

        for day in range(3):
            workout = {
                "name": f"Full Body {day + 1}",
                "exercises": []
            }

            # 1. Компаунд для низу (1 вправа, 3-4 підходи)
            legs = self._select_exercises_smart("ноги", 1, compound_only=True)
            for ex in legs:
                workout["exercises"].append(self._create_exercise_entry(ex, 4))

            # 2. Горизонтальний жим (1 вправа, 3-4 підходи)
            chest = self._select_exercises_smart("грудь", 1, compound_only=True)
            for ex in chest:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            # 3. Горизонтальна тяга (1 вправа, 3-4 підходи)
            back_horizontal = self._select_exercises_smart("спина", 1, compound_only=True)
            for ex in back_horizontal:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            # 4. Вертикальний жим плечі (1 вправа, 3 підходи)
            shoulders = self._select_exercises_smart("плечі", 1, compound_only=True)
            for ex in shoulders:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            # 5. Біцепс (1-2 вправи, 2-3 підходи)
            biceps = self._select_exercises_smart("біцепс", 1)
            for ex in biceps:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            # 6. Трицепс (1-2 вправи, 2-3 підходи)
            triceps = self._select_exercises_smart("трицепс", 1)
            for ex in triceps:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            # 7. Задні дельти або ізоляція плечей (1 вправа, 2-3 підходи)
            rear_delts = self._select_exercises_smart("плечі", 1, isolation_only=True)
            for ex in rear_delts:
                workout["exercises"].append(self._create_exercise_entry(ex, 3))

            workouts.append(workout)

        return workouts

    def _create_upper_lower_4x(self) -> List[Dict]:
        """Upper/Lower 4x тиждень - 6-8 вправ на тренування"""
        upper1 = {"name": "Upper 1", "exercises": []}
        lower1 = {"name": "Lower 1", "exercises": []}
        upper2 = {"name": "Upper 2", "exercises": []}
        lower2 = {"name": "Lower 2", "exercises": []}

        # === UPPER 1 ===
        # Груди компаунд (4 підходи)
        chest1 = self._select_exercises_smart("грудь", 1, compound_only=True)
        for ex in chest1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 4))

        # Спина горизонтальна тяга (4 підходи)
        back1 = self._select_exercises_smart("спина", 1, compound_only=True)
        for ex in back1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 4))

        # Плечі жим (3 підходи)
        shoulders1 = self._select_exercises_smart("плечі", 1, compound_only=True)
        for ex in shoulders1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 3))

        # Груди ізоляція (3 підходи)
        chest_iso1 = self._select_exercises_smart("грудь", 1, isolation_only=True)
        for ex in chest_iso1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 3))

        # Біцепс (2 вправи, 3 підходи кожна)
        biceps1 = self._select_exercises_smart("біцепс", 2)
        for ex in biceps1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 3))

        # Трицепс (2 вправи, 3 підходи кожна)
        triceps1 = self._select_exercises_smart("трицепс", 2)
        for ex in triceps1:
            upper1["exercises"].append(self._create_exercise_entry(ex, 3))

        # === LOWER 1 ===
        # Присідання або жим ногами (4 підходи)
        legs_quad1 = self._select_exercises_smart("ноги", 1, compound_only=True)
        for ex in legs_quad1:
            lower1["exercises"].append(self._create_exercise_entry(ex, 4))

        # Румунська тяга (4 підходи)
        legs_ham1 = self._select_exercises_smart("ноги", 1, target="posterior")
        for ex in legs_ham1:
            lower1["exercises"].append(self._create_exercise_entry(ex, 4))

        # Leg Extension (3 підходи)
        legs_iso1 = self._select_exercises_smart("ноги", 1, isolation_only=True)
        for ex in legs_iso1:
            lower1["exercises"].append(self._create_exercise_entry(ex, 3))

        # Гомілка (3 підходи)
        calves1 = self._select_exercises_smart("ноги", 1, target="calves")
        for ex in calves1:
            lower1["exercises"].append(self._create_exercise_entry(ex, 4))

        # === UPPER 2 ===
        # Груди під кутом (4 підходи)
        chest2 = self._select_exercises_smart("грудь (верх)", 1, compound_only=True)
        for ex in chest2:
            upper2["exercises"].append(self._create_exercise_entry(ex, 4))

        # Спина вертикальна тяга (4 підходи)
        back2 = self._select_exercises_smart("спина", 1, target="width")
        for ex in back2:
            upper2["exercises"].append(self._create_exercise_entry(ex, 4))

        # Плечі бокові дельти (3 підходи)
        shoulders2 = self._select_exercises_smart("плечі", 1, target="lateral")
        for ex in shoulders2:
            upper2["exercises"].append(self._create_exercise_entry(ex, 3))

        # Задні дельти (3 підходи)
        rear_delts = self._select_exercises_smart("плечі", 1, target="rear")
        for ex in rear_delts:
            upper2["exercises"].append(self._create_exercise_entry(ex, 3))

        # Біцепс (2 вправи)
        biceps2 = self._select_exercises_smart("біцепс", 2)
        for ex in biceps2:
            upper2["exercises"].append(self._create_exercise_entry(ex, 3))

        # Трицепс (2 вправи)
        triceps2 = self._select_exercises_smart("трицепс", 2)
        for ex in triceps2:
            upper2["exercises"].append(self._create_exercise_entry(ex, 3))

        # === LOWER 2 ===
        lower2["exercises"] = lower1["exercises"]  # Копіюємо з варіаціями

        return [upper1, lower1, upper2, lower2]

    def _create_ppl_6x(self) -> List[Dict]:
        """Push/Pull/Legs 6x тиждень - професійний обсяг"""
        # TODO: Реалізувати детальний PPL
        return self._create_upper_lower_4x()  # Тимчасово

    def _create_ppl_5x(self) -> List[Dict]:
        """Push/Pull/Legs 5x тиждень"""
        return self._create_upper_lower_4x()  # Тимчасово

    def _create_upper_lower_arms_5x(self) -> List[Dict]:
        """Upper/Lower/Arms 5x тиждень"""
        return self._create_upper_lower_4x()  # Тимчасово

    def _select_exercises_smart(
        self,
        muscle: str,
        count: int,
        compound_only: bool = False,
        isolation_only: bool = False,
        target: str = None
    ) -> List[ExerciseData]:
        """Розумний вибір вправ з фільтрацією"""
        all_exercises = get_exercises_by_muscle(muscle)

        if not all_exercises:
            return []

        # Фільтруємо вже використані
        available = [ex for ex in all_exercises if ex.name not in self.used_exercises]

        if not available:
            self.used_exercises.clear()
            available = all_exercises

        # Фільтруємо по типу
        if compound_only:
            available = [ex for ex in available if self._is_compound(ex)]
        elif isolation_only:
            available = [ex for ex in available if not self._is_compound(ex)]

        # Вибираємо
        random.shuffle(available)
        selected = available[:min(count, len(available))]

        # Додаємо до використаних
        for ex in selected:
            self.used_exercises.add(ex.name)

        return selected

    def _is_compound(self, exercise: ExerciseData) -> bool:
        """Визначає чи вправа компаундна"""
        compound_keywords = [
            "жим", "тяга", "присідання", "станова",
            "підтягування", "віджимання"
        ]
        exercise_lower = exercise.name.lower()
        has_secondary = exercise.secondary_muscles and len(exercise.secondary_muscles.strip()) > 0
        has_compound_keyword = any(kw in exercise_lower for kw in compound_keywords)

        return has_secondary and has_compound_keyword

    def _create_exercise_entry(self, exercise: ExerciseData, sets: int) -> Dict:
        """Створює запис вправи з параметрами"""
        reps, rir = self._determine_reps_and_rir(exercise)

        return {
            "name": exercise.name,
            "sets": sets,
            "reps": reps,
            "rir": rir,
            "target_muscle": exercise.primary_muscle,
            "notes": self._generate_exercise_notes(exercise)
        }

    def _determine_reps_and_rir(self, exercise: ExerciseData) -> Tuple[str, str]:
        """Визначає діапазон повторень та RIR"""
        # Компаундні вправи - менше повторень
        if self._is_compound(exercise):
            return "6-10", "1-2"

        # Ізоляція - більше повторень
        if "махи" in exercise.name.lower() or "розведення" in exercise.name.lower():
            return "12-15", "1-2"

        # Середній діапазон
        return "8-12", "1-2"

    def _generate_exercise_notes(self, exercise: ExerciseData) -> str:
        """Генерує примітки для вправи"""
        return "Повна амплітуда, контрольоване виконання"

    def _generate_professional_notes(self) -> str:
        """Генерує професійні примітки"""
        volume = self.VOLUME_GUIDELINES[self.experience]

        notes = []
        notes.append(f"Мета: {self.goal.name}")
        notes.append(f"Обсяг: {volume['min']}-{volume['max']} підходів на м'яз на тиждень")
        notes.append("RIR 1-2: залишай 1-2 повторення до відмови")
        notes.append("Прогресуй вагу коли досягнеш верхньої межі повторень")
        notes.append("Делод кожні 6-8 тижнів (зниження ваги на 30-40%)")
        notes.append("Відпочинок: компаунд 2-3хв, ізоляція 1-2хв")

        return " | ".join(notes)


def create_professional_program(goal_name: str, workouts_per_week: int, experience: str) -> Dict | None:
    """Створює професійну програму"""
    goal = get_goal_by_name(goal_name)
    if not goal:
        return None

    generator = ProfessionalProgramGenerator(goal, workouts_per_week, experience)
    return generator.generate_program()
