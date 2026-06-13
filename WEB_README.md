# TrainBot Web Application

Flask веб-інтерфейс для TrainBot - фітнес-бота для тренувань.

## Встановлення

1. Встановіть залежності:
```bash
pip install -r requirements_web.txt
```

2. Налаштуйте `.env` файл:
```env
BOT_TOKEN=your_bot_token
DATABASE_URL=sqlite:///training_bot.db
FLASK_SECRET_KEY=your-secret-key-here
FLASK_PORT=5000
```

3. Ініціалізуйте базу даних (якщо ще не зроблено):
```bash
python -c "from sync_database import init_sync_db; init_sync_db()"
```

4. Запустіть веб-додаток:
```bash
python web_app.py
```

Додаток буде доступний за адресою: http://localhost:5000

## Функціонал

- **Авторизація** - вхід через Telegram ID
- **Профіль** - перегляд та редагування особистих даних
- **Програми тренувань** - створення та перегляд програм
- **Тренування** - історія та деталі тренувань
- **Харчування** - відстеження калорій та макронутрієнтів
- **Аналітика** - статистика та персональні рекорди

## Структура

```
trainbot/
├── web_app.py              # Flask додаток
├── sync_database.py        # Sync обгортка для БД
├── templates/              # HTML шаблони
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── profile.html
│   ├── programs.html
│   ├── workouts.html
│   ├── nutrition.html
│   └── analytics.html
└── static/                 # CSS, JS, зображення
    ├── css/
    │   └── style.css
    └── js/
        └── main.js
```

## Примітки

- Використовується та ж база даних, що й бот
- Telegram ID використовується як ідентифікатор користувача
- Веб-інтерфейс працює синхронно (SQLAlchemy без async)
