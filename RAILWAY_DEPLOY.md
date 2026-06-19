# Деплой на Railway

## Налаштування

1. **Створи новий проект на Railway**
   - Зайди на https://railway.app
   - Натисни "New Project"
   - Обери "Deploy from GitHub repo"
   - Підключи репозиторій trainbot

2. **Додай змінні середовища (Environment Variables)**
   У розділі Variables додай:
   ```
   BOT_TOKEN=8844791403:AAGmhCvqKpSYprADcC1g0mOfJuB0kjzhz9s
   DATABASE_URL=sqlite+aiosqlite:///training_bot.db
   FLASK_SECRET_KEY=trainbot-secret-key-2026-change-in-production
   ```

3. **Railway автоматично:**
   - Виявить `Procfile` і запустить `web: python web_app.py`
   - Встановить залежності з `requirements.txt`
   - Використає Python версію з `runtime.txt`

4. **Деплой**
   - Кожен push в GitHub автоматично задеплоїться
   - Або натисни "Deploy" вручну в Railway

## Перевірка роботи

1. **Веб-інтерфейс:**
   - Відкрий URL який дав Railway (наприклад: `https://trainbot.up.railway.app`)
   - Повинна відкритись головна сторінка

2. **Telegram бот:**
   - Напиши `/start` боту в Telegram
   - Бот повинен відповісти

## Логи

Переглядай логи в Railway:
- Клік на сервіс → вкладка "Logs"
- Повинен побачити: "Бот запущено у фоновому потоці"

## Важливо

- Бот працює в одному процесі з веб-сервером
- Використовується polling для отримання повідомлень
- База даних SQLite зберігається всередині контейнера
- При рестарті дані НЕ втрачаються (Railway зберігає volumes)

## Troubleshooting

Якщо бот не працює:
1. Перевір логи в Railway
2. Перевір що BOT_TOKEN правильний
3. Перевір що немає інших інстансів бота (webhook або polling)
