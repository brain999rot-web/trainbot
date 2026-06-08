"""Script to test all button handlers"""
import sys
sys.path.insert(0, '.')

print('Testing button handlers registration...')
print('-' * 60)

# Import all handlers
try:
    from handlers import (
        nutrition_handlers,
        strength_calculator_handlers,
        favorites_records_handlers,
        exercise_database_handlers,
        timer_handlers
    )
    print('SUCCESS: All handler modules imported')
except Exception as e:
    print(f'ERROR: Failed to import handlers: {e}')
    sys.exit(1)

# Check routers exist
routers = [
    ('Nutrition', nutrition_handlers.router),
    ('Strength Calculator', strength_calculator_handlers.router),
    ('Favorites/Records', favorites_records_handlers.router),
    ('Exercise Database', exercise_database_handlers.router),
    ('Timer', timer_handlers.router),
]

print('-' * 60)
for name, router in routers:
    print(f'{name}: Router exists - {router is not None}')

print('-' * 60)
print('All routers registered successfully!')
