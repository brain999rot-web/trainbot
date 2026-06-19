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

3. **Важливо! Отримай публічний URL**
   - Після першого деплою Railway дасть URL (наприклад: `trainbot-production.up.railway.app`)
   - Додай цей URL як змінну:
   ```
   WEBHOOK_URL=https://trainbot-production.up.railway.app
   ```
   - Railway автоматично перезапустить сервіс

4. **Railway автоматично:**
   - Виявить `Procfile` і запустить `web: python web_app.py`
   - Встановить залежності з `requirements.txt`
   - Використає Python версію з `runtime.txt`

## Як це працює

- **Веб-сайт**: Flask сервер на `/`
- **Telegram бот**: Webhook на `/webhook`
- Бот працює через webhook (не polling)
- Telegram надсилає повідомлення на `https://your-url.railway.app/webhook`

## Перевірка роботи

1. **Веб-інтерфейс:**
   - Відкрий Railway URL
   - Повинна відкритись головна сторінка

2. **Telegram бот:**
   - Напиши `/start` боту в Telegram
   - Бот повинен відповісти

3. **Перевірка webhook:**
   - В логах Railway повинно бути: "Встановлюємо webhook: https://..."
   - "Бот готовий до роботи через webhook"

## Логи

Переглядай логи в Railway:
- Клік на сервіс → вкладка "Logs"
- Шукай: "Webhook встановлено" та "Бот готовий"

## Важливо

- Бот використовує **webhook** (не polling)
- Потрібен **HTTPS** URL від Railway
- WEBHOOK_URL встановлюється **після** першого деплою
- База даних SQLite зберігається в volume Railway

## Troubleshooting

### Бот не відповідає:
1. Перевір логи Railway
2. Перевір що `WEBHOOK_URL` встановлено правильно
3. Перевір що `BOT_TOKEN` правильний
4. Відкрий `https://api.telegram.org/bot<BOT_TOKEN>/getWebhookInfo` — перевір webhook

### Помилка "WEBHOOK_URL не встановлено":
1. Додай змінну `WEBHOOK_URL` з твоїм Railway URL
2. Або Railway сам встановить `RAILWAY_STATIC_URL`

### Сайт працює, бот ні:
1. Перевір що webhook встановлено в логах
2. Видали старий webhook: `https://api.telegram.org/bot<BOT_TOKEN>/deleteWebhook`
3. Перезапусти сервіс в Railway
