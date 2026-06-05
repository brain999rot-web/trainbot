from typing import List, Dict, Optional
from dataclasses import dataclass


@dataclass
class ExerciseVariation:
    """Варіація вправи (нахил, хват, тощо)"""
    name: str
    angle: Optional[str] = None  # "30°", "45°", "decline"
    grip: Optional[str] = None  # "широкий", "вузький", "нейтральний", "зворотній"
    description: Optional[str] = None


@dataclass
class ExerciseData:
    name: str
    equipment: str
    primary_muscle: str
    secondary_muscles: str
    difficulty: str
    description: str
    variations: List[ExerciseVariation] = None
    alternative_equipment: List[str] = None  # Альтернативне обладнання

    def __post_init__(self):
        if self.variations is None:
            self.variations = []
        if self.alternative_equipment is None:
            self.alternative_equipment = []


EXERCISE_DATABASE: List[ExerciseData] = [
    # ГРУДЬ
    ExerciseData(
        name="Жим лежа со штангой",
        equipment="штанга, лавка",
        primary_muscle="грудь",
        secondary_muscles="трицепс, передні дельти",
        difficulty="середній",
        description="Базова вправа для грудей"
    ),
    ExerciseData(
        name="Жим лежа з гантелями",
        equipment="гантелі, лавка",
        primary_muscle="грудь",
        secondary_muscles="трицепс, передні дельти",
        difficulty="середній",
        description="Більший діапазон руху ніж зі штангою"
    ),
    ExerciseData(
        name="Жим під кутом зі штангою",
        equipment="штанга, лавка",
        primary_muscle="грудь (верх)",
        secondary_muscles="трицепс, передні дельти",
        difficulty="середній",
        description="Акцент на верх грудей"
    ),
    ExerciseData(
        name="Жим під кутом з гантелями",
        equipment="гантелі, лавка",
        primary_muscle="грудь (верх)",
        secondary_muscles="трицепс, передні дельти",
        difficulty="середній",
        description="Акцент на верх грудей з більшим діапазоном"
    ),
    ExerciseData(
        name="Жим у Сміті під кутом",
        equipment="Машина Сміта, лавка",
        primary_muscle="грудь (верх)",
        secondary_muscles="трицепс, передні дельти",
        difficulty="легкий",
        description="Стабілізована вправа для верху грудей"
    ),
    ExerciseData(
        name="Жим у Сміті горизонтально",
        equipment="Машина Сміта, лавка",
        primary_muscle="грудь",
        secondary_muscles="трицепс, передні дельти",
        difficulty="легкий",
        description="Стабілізований жим"
    ),
    ExerciseData(
        name="Зведення гантелей лежачи",
        equipment="гантелі, лавка",
        primary_muscle="грудь",
        secondary_muscles="передні дельти",
        difficulty="середній",
        description="Ізоляція грудей"
    ),
    ExerciseData(
        name="Зведення на верхньому блоці",
        equipment="кросовер",
        primary_muscle="грудь",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція грудей у кросовері"
    ),
    ExerciseData(
        name="Зведення в кросовері знизу вгору",
        equipment="кросовер",
        primary_muscle="грудь (верх)",
        secondary_muscles="",
        difficulty="легкий",
        description="Акцент на верх грудей"
    ),
    ExerciseData(
        name="Віджимання від підлоги",
        equipment="власна вага",
        primary_muscle="грудь",
        secondary_muscles="трицепс, передні дельти",
        difficulty="легкий",
        description="Базова вправа з власною вагою"
    ),
    ExerciseData(
        name="Віджимання на брусах",
        equipment="бруси/турнік",
        primary_muscle="грудь, трицепс",
        secondary_muscles="передні дельти",
        difficulty="середній",
        description="Компаундна вправа для низу грудей та трицепса"
    ),

    # СПИНА
    ExerciseData(
        name="Підтягування широким хватом",
        equipment="турнік",
        primary_muscle="спина (широта)",
        secondary_muscles="біцепс, задні дельти",
        difficulty="середній",
        description="Базова вправа для ширини спини"
    ),
    ExerciseData(
        name="Підтягування вузьким хватом",
        equipment="турнік",
        primary_muscle="спина",
        secondary_muscles="біцепс",
        difficulty="середній",
        description="Акцент на товщину спини"
    ),
    ExerciseData(
        name="Тяга верхнього блока широким хватом",
        equipment="верхній блок",
        primary_muscle="спина (широта)",
        secondary_muscles="біцепс, задні дельти",
        difficulty="легкий",
        description="Альтернатива підтягуванням"
    ),
    ExerciseData(
        name="Тяга верхнього блока вузьким хватом",
        equipment="верхній блок",
        primary_muscle="спина",
        secondary_muscles="біцепс",
        difficulty="легкий",
        description="Тяга на товщину спини"
    ),
    ExerciseData(
        name="Тяга горизонтального блока",
        equipment="горизонтальний блок",
        primary_muscle="спина (товщина)",
        secondary_muscles="біцепс, задні дельти",
        difficulty="середній",
        description="Базова вправа для товщини спини"
    ),
    ExerciseData(
        name="Тяга гантелі в нахилі",
        equipment="гантелі, лавка",
        primary_muscle="спина",
        secondary_muscles="біцепс, задні дельти",
        difficulty="середній",
        description="Односторонна тяга для спини"
    ),
    ExerciseData(
        name="Тяга штанги в нахилі",
        equipment="штанга",
        primary_muscle="спина (товщина)",
        secondary_muscles="біцепс, задні дельти",
        difficulty="складний",
        description="Потужна базова вправа"
    ),
    ExerciseData(
        name="Тяга у Сміті в нахилі",
        equipment="Машина Сміта",
        primary_muscle="спина",
        secondary_muscles="біцепс, задні дельти",
        difficulty="середній",
        description="Стабілізована тяга"
    ),
    ExerciseData(
        name="Пуловер з гантеллю",
        equipment="гантелі, лавка",
        primary_muscle="спина, грудь",
        secondary_muscles="трицепс",
        difficulty="середній",
        description="Розтяжка широчайших"
    ),

    # ПЛЕЧІ
    ExerciseData(
        name="Жим штанги стоячи",
        equipment="штанга",
        primary_muscle="плечі (передні, середні)",
        secondary_muscles="трицепс",
        difficulty="складний",
        description="Базова вправа для плечей"
    ),
    ExerciseData(
        name="Жим гантелей сидячи",
        equipment="гантелі, лавка",
        primary_muscle="плечі (передні, середні)",
        secondary_muscles="трицепс",
        difficulty="середній",
        description="Жим плечей з гантелями"
    ),
    ExerciseData(
        name="Жим у Сміті сидячи",
        equipment="Машина Сміта, лавка",
        primary_muscle="плечі",
        secondary_muscles="трицепс",
        difficulty="середній",
        description="Стабілізований жим плечей"
    ),
    ExerciseData(
        name="Махи гантелями в сторони",
        equipment="гантелі",
        primary_muscle="плечі (середні)",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція середніх дельт"
    ),
    ExerciseData(
        name="Махи в сторони на нижньому блоці",
        equipment="кросовер",
        primary_muscle="плечі (середні)",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція середніх дельт з постійним натягом"
    ),
    ExerciseData(
        name="Махи гантелями в нахилі",
        equipment="гантелі",
        primary_muscle="плечі (задні)",
        secondary_muscles="",
        difficulty="середній",
        description="Ізоляція задніх дельт"
    ),
    ExerciseData(
        name="Махи в нахилі на верхньому блоці",
        equipment="кросовер",
        primary_muscle="плечі (задні)",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція задніх дельт"
    ),
    ExerciseData(
        name="Підйом штанги перед собою",
        equipment="штанга",
        primary_muscle="плечі (передні)",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція передніх дельт"
    ),
    ExerciseData(
        name="Протяжка штанги до підборіддя",
        equipment="штанга",
        primary_muscle="плечі, трапеції",
        secondary_muscles="біцепс",
        difficulty="середній",
        description="Комплексна вправа для плечей"
    ),

    # БІЦЕПС
    ExerciseData(
        name="Підйом штанги на біцепс стоячи",
        equipment="штанга",
        primary_muscle="біцепс",
        secondary_muscles="передпліччя",
        difficulty="середній",
        description="Базова вправа для біцепса"
    ),
    ExerciseData(
        name="Підйом EZ-грифа на біцепс",
        equipment="EZ-гриф",
        primary_muscle="біцепс",
        secondary_muscles="передпліччя",
        difficulty="легкий",
        description="Зручніший хват для зап'ястків"
    ),
    ExerciseData(
        name="Підйом гантелей на біцепс сидячи",
        equipment="гантелі, лавка",
        primary_muscle="біцепс",
        secondary_muscles="",
        difficulty="середній",
        description="Повна амплітуда для біцепса"
    ),
    ExerciseData(
        name="Молотковий підйом",
        equipment="гантелі",
        primary_muscle="біцепс, брахіаліс",
        secondary_muscles="передпліччя",
        difficulty="легкий",
        description="Розвиток брахіалісу"
    ),
    ExerciseData(
        name="Підйом на біцепс на лавці Скотта",
        equipment="EZ-гриф, лавка Скотта",
        primary_muscle="біцепс",
        secondary_muscles="",
        difficulty="середній",
        description="Ізоляція біцепса"
    ),
    ExerciseData(
        name="Підйом на біцепс на нижньому блоці",
        equipment="кросовер",
        primary_muscle="біцепс",
        secondary_muscles="",
        difficulty="легкий",
        description="Постійне навантаження на біцепс"
    ),
    ExerciseData(
        name="Концентроване згинання",
        equipment="гантелі",
        primary_muscle="біцепс",
        secondary_muscles="",
        difficulty="легкий",
        description="Максимальна ізоляція біцепса"
    ),

    # ТРИЦЕПС
    ExerciseData(
        name="Жим лежачи вузьким хватом",
        equipment="штанга, лавка",
        primary_muscle="трицепс",
        secondary_muscles="грудь, передні дельти",
        difficulty="середній",
        description="Базова вправа для трицепса"
    ),
    ExerciseData(
        name="Французький жим лежачи",
        equipment="EZ-гриф, лавка",
        primary_muscle="трицепс (довга голівка)",
        secondary_muscles="",
        difficulty="середній",
        description="Розтяжка довгої голівки трицепса"
    ),
    ExerciseData(
        name="Французький жим з гантелями",
        equipment="гантелі, лавка",
        primary_muscle="трицепс",
        secondary_muscles="",
        difficulty="середній",
        description="Ізоляція трицепса"
    ),
    ExerciseData(
        name="Розгинання рук на верхньому блоці",
        equipment="верхній блок",
        primary_muscle="трицепс",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція трицепса з постійним натягом"
    ),
    ExerciseData(
        name="Розгинання руки з гантеллю в нахилі",
        equipment="гантелі, лавка",
        primary_muscle="трицепс",
        secondary_muscles="",
        difficulty="легкий",
        description="Односторонна ізоляція"
    ),
    ExerciseData(
        name="Розгинання рук з гантеллю над головою",
        equipment="гантелі",
        primary_muscle="трицепс (довга голівка)",
        secondary_muscles="",
        difficulty="середній",
        description="Розтяжка довгої голівки"
    ),

    # НОГИ
    ExerciseData(
        name="Присідання зі штангою",
        equipment="штанга",
        primary_muscle="квадрицепс, сідниці",
        secondary_muscles="задня поверхня стегна",
        difficulty="складний",
        description="Базова вправа для ніг"
    ),
    ExerciseData(
        name="Присідання у Сміті",
        equipment="Машина Сміта",
        primary_muscle="квадрицепс, сідниці",
        secondary_muscles="задня поверхня стегна",
        difficulty="середній",
        description="Стабілізовані присідання"
    ),
    ExerciseData(
        name="Жим ногами",
        equipment="жим ногами",
        primary_muscle="квадрицепс, сідниці",
        secondary_muscles="задня поверхня стегна",
        difficulty="середній",
        description="Безпечна альтернатива присіданням"
    ),
    ExerciseData(
        name="Розгинання ніг",
        equipment="Leg Extension",
        primary_muscle="квадрицепс",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція квадрицепса"
    ),
    ExerciseData(
        name="Виступи з гантелями",
        equipment="гантелі",
        primary_muscle="квадрицепс, сідниці",
        secondary_muscles="",
        difficulty="середній",
        description="Односторонні присідання"
    ),
    ExerciseData(
        name="Болгарські сплит-присідання",
        equipment="гантелі, лавка",
        primary_muscle="квадрицепс, сідниці",
        secondary_muscles="",
        difficulty="складний",
        description="Інтенсивна односторонна вправа"
    ),

    # ЗАДНЯ ПОВЕРХНЯ СТЕГНА
    ExerciseData(
        name="Румунська тяга зі штангою",
        equipment="штанга",
        primary_muscle="задня поверхня стегна, сідниці",
        secondary_muscles="спина",
        difficulty="середній",
        description="Базова вправа для задньої поверхні"
    ),
    ExerciseData(
        name="Румунська тяга з гантелями",
        equipment="гантелі",
        primary_muscle="задня поверхня стегна, сідниці",
        secondary_muscles="спина",
        difficulty="середній",
        description="Гнучкіша версія румунської тяги"
    ),

    # ТРАПЕЦІЇ
    ExerciseData(
        name="Шраги зі штангою",
        equipment="штанга",
        primary_muscle="трапеції",
        secondary_muscles="",
        difficulty="легкий",
        description="Ізоляція трапецій"
    ),
    ExerciseData(
        name="Шраги з гантелями",
        equipment="гантелі",
        primary_muscle="трапеції",
        secondary_muscles="",
        difficulty="легкий",
        description="Більший діапазон руху"
    ),

    # ПРЕС
    ExerciseData(
        name="Скручування",
        equipment="власна вага",
        primary_muscle="прес",
        secondary_muscles="",
        difficulty="легкий",
        description="Базова вправа для преса"
    ),
    ExerciseData(
        name="Підйом ніг у висі",
        equipment="турнік",
        primary_muscle="прес (низ)",
        secondary_muscles="",
        difficulty="середній",
        description="Вправа для нижньої частини преса"
    ),
    ExerciseData(
        name="Планка",
        equipment="власна вага",
        primary_muscle="прес, кор",
        secondary_muscles="",
        difficulty="легкий",
        description="Статична вправа для кору"
    ),
]


def get_exercises_by_muscle(muscle: str) -> List[ExerciseData]:
    """Повертає список вправ для конкретного м'яза"""
    return [ex for ex in EXERCISE_DATABASE if muscle.lower() in ex.primary_muscle.lower()]


def get_exercise_by_name(name: str) -> ExerciseData | None:
    """Повертає вправу за назвою"""
    for ex in EXERCISE_DATABASE:
        if ex.name.lower() == name.lower():
            return ex
    return None


def get_all_exercises() -> List[ExerciseData]:
    """Повертає всі вправи"""
    return EXERCISE_DATABASE
