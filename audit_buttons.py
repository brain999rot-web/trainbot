"""Complete audit of all buttons and their handlers"""
import sys
import os
sys.path.insert(0, '.')

# Force UTF-8 output
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

print('=' * 70)
print('FULL BUTTON AUDIT - FINAL REPORT')
print('=' * 70)

# All buttons from main keyboard (using ASCII-safe names for checking)
MAIN_MENU_BUTTONS = {
    "Create Program": "🏋 Створити програму",
    "My Program": "📋 Моя програма",
    "Log Workout": "➕ Записати тренування",
    "My Progress": "📈 Мій прогрес",
    "Analytics": "📊 Аналітика",
    "Personal Records": "🏅 Особисті рекорди",
    "TDEE Calculator": "🍽 Калькулятор TDEE",
    "Log Food": "📝 Записати їжу",
    "Nutrition Stats": "📊 Статистика харчування",
    "1RM Calculator": "🏆 Калькулятор 1RM",
    "Exercise Database": "📚 База вправ",
    "Favorites": "⭐ Избранное",
    "Rest Timer": "⏱ Таймер відпочинку",
    "Settings": "⚙ Налаштування",
    "Help": "📚 Довідка",
}

# Expected handlers mapping (CORRECTED FUNCTION NAMES)
EXPECTED_HANDLERS = {
    "Create Program": ("program_handlers", "create_program_start"),
    "My Program": ("program_handlers", "view_program"),
    "Log Workout": ("workout_handlers", "start_workout_logging"),
    "My Progress": ("progress_handlers", "show_progress"),
    "Analytics": ("analytics_handlers", "show_analytics"),
    "Personal Records": ("favorites_records_handlers", "show_personal_records"),
    "TDEE Calculator": ("nutrition_handlers", "start_tdee_calculator"),
    "Log Food": ("nutrition_handlers", "start_nutrition_logging"),
    "Nutrition Stats": ("nutrition_handlers", "show_nutrition_stats"),
    "1RM Calculator": ("strength_calculator_handlers", "start_1rm_calculator"),
    "Exercise Database": ("exercise_database_handlers", "show_exercise_database"),
    "Favorites": ("favorites_records_handlers", "show_favorites"),
    "Rest Timer": ("timer_handlers", "timer_menu"),
    "Settings": ("registration", "settings_handler"),
    "Help": ("registration", "help_handler"),
}

print(f'\nTotal buttons to check: {len(MAIN_MENU_BUTTONS)}')
print('-' * 70)

# Import all handlers
from handlers import (
    registration,
    program_handlers,
    workout_handlers,
    progress_handlers,
    analytics_handlers,
    timer_handlers,
    exercise_database_handlers,
    strength_calculator_handlers,
    favorites_records_handlers,
    nutrition_handlers
)

handlers_map = {
    'registration': registration,
    'program_handlers': program_handlers,
    'workout_handlers': workout_handlers,
    'progress_handlers': progress_handlers,
    'analytics_handlers': analytics_handlers,
    'timer_handlers': timer_handlers,
    'exercise_database_handlers': exercise_database_handlers,
    'strength_calculator_handlers': strength_calculator_handlers,
    'favorites_records_handlers': favorites_records_handlers,
    'nutrition_handlers': nutrition_handlers,
}

results = {
    'working': [],
    'missing': [],
    'errors': []
}

for button_name, button_text in MAIN_MENU_BUTTONS.items():
    if button_name not in EXPECTED_HANDLERS:
        results['missing'].append((button_name, 'No handler mapping defined'))
        continue

    module_name, handler_name = EXPECTED_HANDLERS[button_name]

    try:
        module = handlers_map.get(module_name)
        if module is None:
            results['errors'].append((button_name, f'Module {module_name} not found'))
            continue

        if hasattr(module, handler_name):
            results['working'].append((button_name, module_name, handler_name))
        else:
            results['missing'].append((button_name, f'{module_name}.{handler_name} not found'))
    except Exception as e:
        results['errors'].append((button_name, str(e)))

print('\nALL BUTTONS STATUS:')
print('-' * 70)
for button, module, handler in sorted(results['working']):
    print(f'[OK] {button}')
    print(f'     Handler: {module}.{handler}')

if results['missing']:
    print('\nMISSING HANDLERS:')
    print('-' * 70)
    for button, reason in results['missing']:
        print(f'[MISSING] {button}')
        print(f'          {reason}')

if results['errors']:
    print('\nERRORS:')
    print('-' * 70)
    for button, error in results['errors']:
        print(f'[ERROR] {button}')
        print(f'        {error}')

print('\n' + '=' * 70)
print(f'FINAL RESULT: {len(results["working"])}/{len(MAIN_MENU_BUTTONS)} buttons working')
if len(results['missing']) == 0 and len(results['errors']) == 0:
    print('STATUS: ALL BUTTONS HAVE WORKING HANDLERS!')
else:
    print(f'Missing: {len(results["missing"])}')
    print(f'Errors: {len(results["errors"])}')
print('=' * 70)

sys.exit(0 if len(results['missing']) == 0 and len(results['errors']) == 0 else 1)
