from typing import Dict, List, Tuple
from utils.goals import Goal, get_goal_by_name
from utils.exercise_database import get_exercises_by_muscle, ExerciseData
import random


class ProgramGenerator:
    """Генератор тренувальних програм"""

    def __init__(self, goal: Goal, workouts_per_week: int, experience: str):
        self.goal = goal
        self.workouts_per_week = workouts_per_week
        self.experience = experience

    def generate_program(self) -> Dict:
        """Генерує повну тренувальну програму"""
        split_type = self._determine_split()
        workouts = self._create_workouts(split_type)

        return {
            "goal": self.goal.name,
            "split_type": split_type,
            "workouts_per_week": self.workouts_per_week,
            "workouts": workouts,
            "notes": self._generate_notes()
        }

    def _determine_split(self) -> str:
        """Визначає оптимальний сплит"""
        if self.workouts_per_week <= 3:
            return "Full Body"
        elif self.workouts_per_week == 4:
            if "Upper Lower" in self.goal.recommended_split:
                return "Upper Lower"
            return "Upper Lower"
        elif self.workouts_per_week == 5:
            if "Arms" in self.goal.recommended_split:
                return "Upper Lower Arms"
            return "Push Pull Legs"
        else:  # 6
            return "Push Pull Legs"

    def _create_workouts(self, split_type: str) -> List[Dict]:
        """Створює тренування відповідно до сплиту"""
        if split_type == "Full Body":
            return self._create_full_body_split()
        elif split_type == "Upper Lower":
            return self._create_upper_lower_split()
        elif split_type == "Upper Lower Arms":
            return self._create_upper_lower_arms_split()
        elif split_type == "Push Pull Legs":
            return self._create_push_pull_legs_split()
        elif split_type == "Push Pull Arms":
            return self._create_push_pull_arms_split()
        return []

    def _create_full_body_split(self) -> List[Dict]:
        """Full Body сплит (3 тренування)"""
        workouts = []
        for i in range(3):
            workout = {
                "name": f"Full Body {i+1}",
                "exercises": []
            }

            # Додаємо вправи для кожної м'язової групи
            muscle_groups = ["грудь", "спина", "плечі", "біцепс", "трицепс", "ноги"]
            for muscle in muscle_groups:
                if muscle in self.goal.muscle_priorities:
                    sets = 3 if self.goal.muscle_priorities[muscle].priority == "high" else 2
                    exercises = self._select_exercises(muscle, 1)
                    for ex in exercises:
                        workout["exercises"].append(self._create_exercise_entry(ex, sets))

            workouts.append(workout)
        return workouts

    def _create_upper_lower_split(self) -> List[Dict]:
        """Upper Lower сплит (4 тренування)"""
        upper1 = {
            "name": "Upper 1",
            "exercises": []
        }
        upper2 = {
            "name": "Upper 2",
            "exercises": []
        }
        lower1 = {
            "name": "Lower 1",
            "exercises": []
        }
        lower2 = {
            "name": "Lower 2",
            "exercises": []
        }

        # Upper 1: груди, спина, плечі, біцепс, трицепс
        upper_muscles = ["грудь", "спина", "плечі", "біцепс", "трицепс"]
        for muscle in upper_muscles:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, max(1, sets_per_workout // 4))

                for ex in exercises:
                    upper1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Upper 2: варіації
        for muscle in upper_muscles:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, max(1, sets_per_workout // 4), exclude_from_upper1=True)

                for ex in exercises:
                    upper2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Lower 1 і Lower 2
        leg_exercises = self._select_exercises("ноги", 3)
        for i, ex in enumerate(leg_exercises):
            if i < 2:
                lower1["exercises"].append(self._create_exercise_entry(ex, 4))
            else:
                lower2["exercises"].append(self._create_exercise_entry(ex, 4))

        return [upper1, lower1, upper2, lower2]

    def _create_upper_lower_arms_split(self) -> List[Dict]:
        """Upper Lower Arms сплит (5 тренувань)"""
        upper = {"name": "Upper", "exercises": []}
        lower = {"name": "Lower", "exercises": []}
        arms1 = {"name": "Arms 1", "exercises": []}
        upper2 = {"name": "Upper 2", "exercises": []}
        arms2 = {"name": "Arms 2", "exercises": []}

        # Upper: груди, спина, плечі
        for muscle in ["грудь", "спина", "плечі"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    upper["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Lower
        leg_exercises = self._select_exercises("ноги", 4)
        for ex in leg_exercises:
            lower["exercises"].append(self._create_exercise_entry(ex, 3))

        # Arms 1: біцепс + трицепс
        for muscle in ["біцепс", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 3)
                for ex in exercises:
                    arms1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Upper 2
        for muscle in ["грудь", "спина", "плечі"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    upper2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Arms 2
        for muscle in ["біцепс", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 3)
                for ex in exercises:
                    arms2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        return [upper, lower, arms1, upper2, arms2]

    def _create_push_pull_legs_split(self) -> List[Dict]:
        """Push Pull Legs сплит (5-6 тренувань)"""
        push1 = {"name": "Push 1", "exercises": []}
        pull1 = {"name": "Pull 1", "exercises": []}
        legs1 = {"name": "Legs 1", "exercises": []}
        push2 = {"name": "Push 2", "exercises": []}
        pull2 = {"name": "Pull 2", "exercises": []}

        # Push: груди, плечі, трицепс
        for muscle in ["грудь", "плечі", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    push1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Pull: спина, біцепс
        for muscle in ["спина", "біцепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    pull1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Legs
        leg_exercises = self._select_exercises("ноги", 4)
        for ex in leg_exercises:
            legs1["exercises"].append(self._create_exercise_entry(ex, 3))

        # Push 2
        for muscle in ["грудь", "плечі", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    push2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Pull 2
        for muscle in ["спина", "біцепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 2)
                for ex in exercises:
                    pull2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        if self.workouts_per_week == 6:
            legs2 = {"name": "Legs 2", "exercises": []}
            leg_exercises2 = self._select_exercises("ноги", 3)
            for ex in leg_exercises2:
                legs2["exercises"].append(self._create_exercise_entry(ex, 3))
            return [push1, pull1, legs1, push2, pull2, legs2]

        return [push1, pull1, legs1, push2, pull2]

    def _create_push_pull_arms_split(self) -> List[Dict]:
        """Push Pull Arms сплит (5-6 тренувань)"""
        push1 = {"name": "Push 1", "exercises": []}
        pull1 = {"name": "Pull 1", "exercises": []}
        arms1 = {"name": "Arms 1", "exercises": []}
        push2 = {"name": "Push 2", "exercises": []}
        pull2 = {"name": "Pull 2", "exercises": []}

        # Push: груди, плечі
        for muscle in ["грудь", "плечі"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 3)
                for ex in exercises:
                    push1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Pull: спина
        if "спина" in self.goal.muscle_priorities:
            vol = self.goal.muscle_priorities["спина"]
            sets_per_workout = self._calculate_sets_per_workout(vol, 2)
            exercises = self._select_exercises("спина", 4)
            for ex in exercises:
                pull1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Arms 1
        for muscle in ["біцепс", "трицепс"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 3)
                for ex in exercises:
                    arms1["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Push 2
        for muscle in ["грудь", "плечі"]:
            if muscle in self.goal.muscle_priorities:
                vol = self.goal.muscle_priorities[muscle]
                sets_per_workout = self._calculate_sets_per_workout(vol, 2)
                exercises = self._select_exercises(muscle, 3)
                for ex in exercises:
                    push2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        # Pull 2
        if "спина" in self.goal.muscle_priorities:
            vol = self.goal.muscle_priorities["спина"]
            sets_per_workout = self._calculate_sets_per_workout(vol, 2)
            exercises = self._select_exercises("спина", 4)
            for ex in exercises:
                pull2["exercises"].append(self._create_exercise_entry(ex, sets_per_workout // len(exercises)))

        return [push1, pull1, arms1, push2, pull2]

    def _calculate_sets_per_workout(self, volume: 'MuscleVolume', frequency: int) -> int:
        """Розраховує кількість підходів на тренування"""
        avg_weekly_sets = (volume.min_sets + volume.max_sets) // 2
        return max(3, avg_weekly_sets // frequency)

    def _select_exercises(self, muscle: str, count: int, exclude_from_upper1: bool = False) -> List[ExerciseData]:
        """Вибирає вправи для м'яза"""
        all_exercises = get_exercises_by_muscle(muscle)
        if not all_exercises:
            return []

        # Перемішуємо та вибираємо
        random.shuffle(all_exercises)
        return all_exercises[:min(count, len(all_exercises))]

    def _create_exercise_entry(self, exercise: ExerciseData, sets: int) -> Dict:
        """Створює запис вправи з параметрами"""
        reps, rir = self._determine_reps_and_rir(exercise)

        return {
            "name": exercise.name,
            "sets": max(2, sets),
            "reps": reps,
            "rir": rir,
            "target_muscle": exercise.primary_muscle,
            "notes": self._generate_exercise_notes(exercise)
        }

    def _determine_reps_and_rir(self, exercise: ExerciseData) -> Tuple[str, str]:
        """Визначає діапазон повторень та RIR"""
        # Базові вправи - менше повторень
        if "жим" in exercise.name.lower() or "присідання" in exercise.name.lower() or "тяга" in exercise.name.lower():
            if "штанга" in exercise.equipment.lower():
                return "6-10", "1-2"
            return "8-12", "1-2"

        # Ізоляція - більше повторень
        if "махи" in exercise.name.lower() or "зведення" in exercise.name.lower() or "підйом" in exercise.name.lower():
            return "12-15", "1-3"

        # За замовчуванням
        return "8-12", "1-2"

    def _generate_exercise_notes(self, exercise: ExerciseData) -> str:
        """Генерує примітки для вправи"""
        notes = []

        if "жим" in exercise.name.lower() and "під кутом" in exercise.name.lower():
            notes.append("Кут лавки 30-45°")

        if "підтягування" in exercise.name.lower():
            notes.append("Можна використовувати допомогу або обтяжлення")

        if "махи" in exercise.name.lower():
            notes.append("Контрольована амплітуда, без інерції")

        if exercise.primary_muscle == "біцепс" or exercise.primary_muscle == "трицепс":
            notes.append("Повна амплітуда руху")

        return "; ".join(notes) if notes else "Виконувати технічно"

    def _generate_notes(self) -> str:
        """Генерує загальні примітки до програми"""
        notes = []
        notes.append(f"Програма розроблена під мету: {self.goal.name}")
        notes.append(f"Сплит: {self._determine_split()}")
        notes.append("Використовуйте прогресивне перевантаження")
        notes.append("RIR 1-2 означає залишити 1-2 повторення до відмови")
        notes.append("Збільшуйте вагу коли досягли верхньої межі повторень у всіх підходах")
        notes.append("Делод кожні 6-10 тижнів")
        return " | ".join(notes)


def create_program(goal_name: str, workouts_per_week: int, experience: str) -> Dict | None:
    """Створює програму тренувань"""
    goal = get_goal_by_name(goal_name)
    if not goal:
        return None

    generator = ProgramGenerator(goal, workouts_per_week, experience)
    return generator.generate_program()
