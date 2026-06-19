from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class MuscleVolume:
    """Обсяг тренування для групи м'язів"""
    min_sets: int
    max_sets: int
    priority: str  # "high", "medium", "low"


@dataclass
class Goal:
    """Тренувальна мета"""
    name: str
    description: str
    muscle_priorities: Dict[str, MuscleVolume]
    recommended_frequency: int
    recommended_split: str


TRAINING_GOALS: List[Goal] = [
    Goal(
        name="Великі руки",
        description="Максимальний розвиток біцепса та трицепса",
        muscle_priorities={
            "біцепс": MuscleVolume(16, 24, "high"),
            "трицепс": MuscleVolume(16, 24, "high"),
            "грудь": MuscleVolume(8, 12, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(6, 10, "low"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Arms"
    ),
    Goal(
        name="Величезний біцепс",
        description="Спеціалізація на біцепс",
        muscle_priorities={
            "біцепс": MuscleVolume(20, 26, "high"),
            "трицепс": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(8, 12, "medium"),
            "плечі": MuscleVolume(8, 12, "medium"),
            "ноги": MuscleVolume(6, 10, "low"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Arms"
    ),
    Goal(
        name="Величезний трицепс",
        description="Спеціалізація на трицепс",
        muscle_priorities={
            "трицепс": MuscleVolume(20, 26, "high"),
            "біцепс": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(6, 10, "low"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Arms"
    ),
    Goal(
        name="Домінантні руки",
        description="Руки як головний акцент фізики",
        muscle_priorities={
            "біцепс": MuscleVolume(18, 24, "high"),
            "трицепс": MuscleVolume(18, 24, "high"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Arms"
    ),
    Goal(
        name="Домінантні плечі",
        description="Максимальний розвиток дельт",
        muscle_priorities={
            "плечі": MuscleVolume(20, 26, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Домінантні плечі + руки",
        description="Акцент на верхню частину рук та плечі",
        muscle_priorities={
            "плечі": MuscleVolume(18, 24, "high"),
            "біцепс": MuscleVolume(16, 22, "high"),
            "трицепс": MuscleVolume(16, 22, "high"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(6, 10, "low"),
        },
        recommended_frequency=6,
        recommended_split="Push Pull Arms"
    ),
    Goal(
        name="Широкі плечі",
        description="Розвиток середніх дельт для ширини",
        muscle_priorities={
            "плечі": MuscleVolume(18, 24, "high"),
            "спина": MuscleVolume(14, 18, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="3D-плечі",
        description="Повний розвиток усіх пучків дельт",
        muscle_priorities={
            "плечі": MuscleVolume(20, 26, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="V-подібна фігура",
        description="Широка спина та плечі, вузька талія",
        muscle_priorities={
            "спина": MuscleVolume(18, 24, "high"),
            "плечі": MuscleVolume(16, 22, "high"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Широка спина",
        description="Розвиток ширини спини (широчайші)",
        muscle_priorities={
            "спина": MuscleVolume(20, 26, "high"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Товста спина",
        description="Розвиток товщини спини",
        muscle_priorities={
            "спина": MuscleVolume(20, 26, "high"),
            "трапеції": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Великі груди",
        description="Максимальний розвиток грудних м'язів",
        muscle_priorities={
            "грудь": MuscleVolume(20, 26, "high"),
            "трицепс": MuscleVolume(14, 18, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "біцепс": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Верх грудей",
        description="Спеціалізація на верхню частину грудей",
        muscle_priorities={
            "грудь": MuscleVolume(20, 26, "high"),
            "плечі": MuscleVolume(14, 18, "medium"),
            "трицепс": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "біцепс": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Акцент на груди",
        description="Груди як пріоритет у збалансованій програмі",
        muscle_priorities={
            "грудь": MuscleVolume(18, 22, "high"),
            "спина": MuscleVolume(14, 18, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Акцент на спину",
        description="Спина як пріоритет у збалансованій програмі",
        muscle_priorities={
            "спина": MuscleVolume(18, 22, "high"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Акцент на плечі",
        description="Плечі як пріоритет у збалансованій програмі",
        muscle_priorities={
            "плечі": MuscleVolume(18, 22, "high"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(14, 18, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Акцент на руки",
        description="Руки як пріоритет у збалансованій програмі",
        muscle_priorities={
            "біцепс": MuscleVolume(16, 20, "high"),
            "трицепс": MuscleVolume(16, 20, "high"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Arms"
    ),
    Goal(
        name="Акцент на ноги",
        description="Ноги як пріоритет",
        muscle_priorities={
            "ноги": MuscleVolume(18, 24, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Естетика",
        description="Класична естетична фізика",
        muscle_priorities={
            "грудь": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(14, 18, "high"),
            "плечі": MuscleVolume(14, 18, "high"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Менс-фізік стиль",
        description="Акцент на верх тіла, естетичні пропорції",
        muscle_priorities={
            "плечі": MuscleVolume(16, 20, "high"),
            "спина": MuscleVolume(16, 20, "high"),
            "грудь": MuscleVolume(14, 18, "high"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Пляжне тіло",
        description="Візуально атлетична фігура",
        muscle_priorities={
            "грудь": MuscleVolume(14, 18, "high"),
            "плечі": MuscleVolume(14, 18, "high"),
            "руки": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
            "прес": MuscleVolume(6, 10, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Рекомпозиція",
        description="Одночасне спалювання жиру та набір м'язів",
        muscle_priorities={
            "грудь": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(12, 16, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Сушка",
        description="Збереження м'язів під час дефіциту калорій",
        muscle_priorities={
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(8, 12, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=3,
        recommended_split="Full Body"
    ),
    Goal(
        name="Набір маси",
        description="Максимальний набір м'язової маси",
        muscle_priorities={
            "грудь": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(14, 18, "high"),
            "плечі": MuscleVolume(14, 18, "high"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(14, 18, "high"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Максимальна гіпертрофія",
        description="Повний розвиток усіх м'язових груп",
        muscle_priorities={
            "грудь": MuscleVolume(16, 20, "high"),
            "спина": MuscleVolume(16, 20, "high"),
            "плечі": MuscleVolume(16, 20, "high"),
            "руки": MuscleVolume(14, 18, "high"),
            "ноги": MuscleVolume(16, 20, "high"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Силовий ухил",
        description="Гіпертрофія з акцентом на силу",
        muscle_priorities={
            "грудь": MuscleVolume(12, 16, "high"),
            "спина": MuscleVolume(12, 16, "high"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(12, 16, "high"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Силовий жим",
        description="Максимальний розвиток жимових м'язів",
        muscle_priorities={
            "грудь": MuscleVolume(16, 20, "high"),
            "трицепс": MuscleVolume(14, 18, "high"),
            "плечі": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "біцепс": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Сильні руки",
        description="Сила та маса рук",
        muscle_priorities={
            "біцепс": MuscleVolume(14, 18, "high"),
            "трицепс": MuscleVolume(14, 18, "high"),
            "передпліччя": MuscleVolume(8, 12, "medium"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Верх тіла",
        description="Фокус на верхню частину тіла",
        muscle_priorities={
            "грудь": MuscleVolume(16, 20, "high"),
            "спина": MuscleVolume(16, 20, "high"),
            "плечі": MuscleVolume(14, 18, "high"),
            "руки": MuscleVolume(14, 18, "high"),
            "ноги": MuscleVolume(6, 10, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Спина + плечі",
        description="Акцент на задню частину верху тіла",
        muscle_priorities={
            "спина": MuscleVolume(18, 22, "high"),
            "плечі": MuscleVolume(18, 22, "high"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Груди + руки",
        description="Класична комбінація для масивного верху",
        muscle_priorities={
            "грудь": MuscleVolume(18, 22, "high"),
            "біцепс": MuscleVolume(16, 20, "high"),
            "трицепс": MuscleVolume(16, 20, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Arms"
    ),
    Goal(
        name="Плечі + груди",
        description="Потужна передня частина верху тіла",
        muscle_priorities={
            "плечі": MuscleVolume(18, 22, "high"),
            "грудь": MuscleVolume(18, 22, "high"),
            "трицепс": MuscleVolume(14, 18, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "біцепс": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Legs"
    ),
    Goal(
        name="Руки + спина",
        description="Масивна задня частина верху тіла",
        muscle_priorities={
            "біцепс": MuscleVolume(18, 22, "high"),
            "спина": MuscleVolume(18, 22, "high"),
            "трицепс": MuscleVolume(14, 18, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Push Pull Arms"
    ),
    Goal(
        name="Збалансований розвиток",
        description="Гармонійний розвиток усього тіла",
        muscle_priorities={
            "грудь": MuscleVolume(12, 16, "medium"),
            "спина": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(12, 16, "medium"),
            "ноги": MuscleVolume(12, 16, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Атлетична фігура",
        description="Спортивне тіло з акцентом на функціональність",
        muscle_priorities={
            "спина": MuscleVolume(14, 18, "high"),
            "ноги": MuscleVolume(14, 18, "high"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
            "прес": MuscleVolume(8, 12, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Full Body"
    ),
    Goal(
        name="Кроссфіт база",
        description="Розвиток сили та витривалості для функціонального тренінгу",
        muscle_priorities={
            "ноги": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(14, 18, "high"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(12, 16, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
            "прес": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Full Body"
    ),
    Goal(
        name="Сильні ноги",
        description="Максимальна маса та сила ніг",
        muscle_priorities={
            "ноги": MuscleVolume(20, 26, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Legs"
    ),
    Goal(
        name="Потужні квадрицепси",
        description="Спеціалізація на передню поверхню стегна",
        muscle_priorities={
            "ноги": MuscleVolume(22, 28, "high"),
            "спина": MuscleVolume(10, 14, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=5,
        recommended_split="Upper Lower Legs"
    ),
    Goal(
        name="Сідниці та ноги",
        description="Акцент на розвиток ніг та сідниць",
        muscle_priorities={
            "ноги": MuscleVolume(20, 26, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(8, 12, "low"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Міцний прес",
        description="Розвиток м'язів кору та преса",
        muscle_priorities={
            "прес": MuscleVolume(14, 18, "high"),
            "спина": MuscleVolume(12, 16, "medium"),
            "грудь": MuscleVolume(12, 16, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(10, 14, "medium"),
            "ноги": MuscleVolume(12, 16, "medium"),
        },
        recommended_frequency=4,
        recommended_split="Upper Lower"
    ),
    Goal(
        name="Початківець",
        description="Вивчення техніки та адаптація організму",
        muscle_priorities={
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(8, 12, "medium"),
            "руки": MuscleVolume(8, 12, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=3,
        recommended_split="Full Body"
    ),
    Goal(
        name="Повернення після перерви",
        description="Відновлення форми після тривалої паузи",
        muscle_priorities={
            "грудь": MuscleVolume(10, 14, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(10, 14, "medium"),
            "руки": MuscleVolume(8, 12, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
        },
        recommended_frequency=3,
        recommended_split="Full Body"
    ),
    Goal(
        name="Витривалість та тонус",
        description="Підтримка форми з фокусом на витривалість",
        muscle_priorities={
            "грудь": MuscleVolume(8, 12, "medium"),
            "спина": MuscleVolume(10, 14, "medium"),
            "плечі": MuscleVolume(8, 12, "medium"),
            "руки": MuscleVolume(8, 12, "medium"),
            "ноги": MuscleVolume(10, 14, "medium"),
            "прес": MuscleVolume(8, 12, "medium"),
        },
        recommended_frequency=3,
        recommended_split="Full Body"
    ),
    Goal(
        name="Підтримка форми",
        description="Збереження результатів при обмеженому часі",
        muscle_priorities={
            "грудь": MuscleVolume(8, 12, "medium"),
            "спина": MuscleVolume(8, 12, "medium"),
            "плечі": MuscleVolume(8, 12, "medium"),
            "руки": MuscleVolume(6, 10, "low"),
            "ноги": MuscleVolume(8, 12, "medium"),
        },
        recommended_frequency=3,
        recommended_split="Full Body"
    ),
]


def get_goal_by_name(goal_name: str) -> Goal | None:
    """Повертає мету за назвою"""
    for goal in TRAINING_GOALS:
        if goal.name.lower() == goal_name.lower():
            return goal
    return None


def get_all_goals() -> List[Goal]:
    """Повертає всі доступні цілі"""
    return TRAINING_GOALS


def get_goals_names() -> List[str]:
    """Повертає список назв усіх цілей"""
    return [goal.name for goal in TRAINING_GOALS]
