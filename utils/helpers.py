def format_weight(weight: float) -> str:
    """Форматує вагу для відображення"""
    if weight == int(weight):
        return str(int(weight))
    return f"{weight:.1f}"


def calculate_weight_increase(current_weight: float, percentage: float = 2.5) -> float:
    """Розраховує збільшення ваги"""
    increase = current_weight * (percentage / 100)
    # Округлюємо до найближчих 0.5 кг
    return round(increase * 2) / 2


def parse_reps_range(reps_str: str) -> tuple[int, int]:
    """Парсить діапазон повторень"""
    if "-" in reps_str:
        min_reps, max_reps = map(int, reps_str.split("-"))
        return min_reps, max_reps
    else:
        reps = int(reps_str)
        return reps, reps


def is_in_rep_range(reps: int, target_range: str) -> bool:
    """Перевіряє чи повторення в цільовому діапазоні"""
    min_reps, max_reps = parse_reps_range(target_range)
    return min_reps <= reps <= max_reps


def format_date(dt) -> str:
    """Форматує дату для відображення"""
    return dt.strftime("%d.%m.%Y %H:%M")


def calculate_volume(sets: list[dict]) -> float:
    """Розраховує об'єм навантаження (вага * повторення * підходи)"""
    return sum(s["weight"] * s["reps"] for s in sets)
