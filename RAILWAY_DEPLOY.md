# TrainBot - Deployment на Railway

## Швидкий деплой

### 1. Створіть проєкт на Railway

1. Зайдіть на [railway.app](https://railway.app)
2. Натисніть "New Project" → "Deploy from GitHub repo"
3. Оберіть репозиторій trainbot

### 2. Налаштуйте змінні середовища

Додайте в Railway Dashboard → Variables:

```env
BOT_TOKEN=your_bot_token_from_botfather
DATABASE_URL=sqlite:///training_bot.db
FLASK_SECRET_KEY=your-random-secret-key-here
PORT=5000
```

### 3. Деплой

Railway автоматично задеплоїть додаток після push в GitHub.

## Структура проєкту

- **bot.py** - Telegram бот (aiogram)
- **web_app.py** - Flask веб-інтерфейс
- **requirements.txt** - Всі залежності (бот + веб)
- **Procfile** - Команди запуску для Railway
- **railway.json** - Конфігурація Railway

## Запуск локально

### Бот:
```bash
python bot.py
```

### Веб-додаток:
```bash
python web_app.py
```

Веб-інтерфейс: http://localhost:5000

## Railway - два сервіси

Для запуску і бота, і веб-додатку одночасно на Railway:

1. Створіть **два окремі сервіси** в одному проєкті
2. Перший сервіс (Bot):
   - Start Command: `python bot.py`
   - Змінні: BOT_TOKEN, DATABASE_URL
3. Другий сервіс (Web):
   - Start Command: `python web_app.py`
   - Змінні: FLASK_SECRET_KEY, PORT, DATABASE_URL

Або використовуйте **Railway volumes** для спільної бази даних SQLite між сервісами.

## База даних

За замовчуванням використовується SQLite. Для production розгляньте PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@host:5432/trainbot
```

Оновіть `database.py` та `sync_database.py` для PostgreSQL драйверів.

## Troubleshooting

### Flask не запускається
- Перевірте що PORT встановлено в змінних Railway
- Перевірте що Flask встановлено в requirements.txt

### База даних не зберігається
- Railway ephemeral filesystem - додайте Railway Volume
- Або використовуйте PostgreSQL замість SQLite

### Бот та веб не бачать одну БД
- Використовуйте спільний Railway Volume
- Або винесіть БД на окремий PostgreSQL сервіс
