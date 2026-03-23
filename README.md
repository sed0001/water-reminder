# Water Reminder Bot

Telegram-бот для напоминания пить воду.

## Описание

Бот отправляет напоминание «Выпей воды!» каждые 30 минут в период с 10:00 до 21:00 по московскому времени.

## Функции

- `/start` — добавить пользователя в список активных и начать получать напоминания
- `/stop` — удалить пользователя из списка активных и прекратить получать напоминания
- Напоминания отправляются автоматически каждые 30 минут

## Установка

### 1. Клонирование репозитория

```bash
cd water-reminder
```

### 2. Создание виртуального окружения

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 4. Настройка токена бота

1. Создайте файл `.env` в корневой папке проекта
2. Скопируйте содержимое из `.env.example`
3. Замените `your_bot_token_here` на токен вашего бота, полученный от [@BotFather](https://t.me/BotFather)

Пример файла `.env`:
```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
```

## Запуск

```bash
python bot.py
```

При первом запуске автоматически создаётся база данных SQLite `water_reminder.db`.

## Требования

- Python 3.9+
- aiogram 3.x
- python-dotenv
