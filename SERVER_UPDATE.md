# Інструкція для оновлення бота на сервері

## 🚀 Швидке оновлення

```bash
# 1. Зупини бота (залежить від твого методу запуску)
# Якщо systemd:
sudo systemctl stop trainbot

# Якщо screen/tmux:
screen -r trainbot  # потім Ctrl+C

# Якщо docker:
docker-compose down

# 2. Оновити код
cd /path/to/trainbot
git pull origin main

# 3. Запусти бота знову
# Якщо systemd:
sudo systemctl start trainbot

# Якщо screen:
screen -dmS trainbot python bot.py

# Якщо docker:
docker-compose up -d
```

## ✅ Що виправлено

1. Видалено дублікат `/menu` handler
2. Розділено `📝 Записати їжу` на окремі message/callback handlers
3. Додано команду `/menu` для відновлення клавіатури

## 🧪 Як перевірити

Після перезапуску натисни кнопки:
- 🏆 Калькулятор 1RM
- 📚 База вправ
- ⏱ Таймер відпочинку
- 📝 Записати їжу
- 📊 Статистика харчування
- 🏅 Особисті рекорди

Всі мають відповідати!

## 📝 Логи

Якщо не працює, перевір логи:
```bash
# Systemd
sudo journalctl -u trainbot -f

# Docker
docker-compose logs -f

# Screen
screen -r trainbot
```

---
**Оновлено:** 2026-06-06 18:50
