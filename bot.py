"""
Основной файл Telegram-бота для напоминания пить воду.
"""
import asyncio
import logging
from datetime import datetime, time

from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import Command
from dotenv import load_dotenv
import os

# Импорт модуля работы с базой данных
import database

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Загрузка переменных окружения
load_dotenv()

# Получение токена бота из переменной окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    logger.error("Токен бота не найден! Убедитесь, что файл .env содержит BOT_TOKEN")
    exit(1)

# Инициализация бота и диспетчера
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

# Регистрация роутера
dp.include_router(router)

# Временной интервал для напоминаний (по московскому времени)
REMINDER_START_HOUR = 10  # 10:00
REMINDER_END_HOUR = 21    # 21:00
REMINDER_INTERVAL = 30    # Интервал в минутах


def is_reminder_time() -> bool:
    """
    Проверяет, находится ли текущее время в интервале для напоминаний.
    Использует московское время (UTC+3).
    
    Returns:
        True, если текущее время в интервале 10:00-21:00; иначе False.
    """
    # Получаем текущее время в московском часовом поясе (UTC+3)
    # Для простоты используем смещение +3 часа от UTC
    moscow_time = datetime.utcnow().hour + 3
    
    # Корректировка, если время перешло через сутки
    if moscow_time >= 24:
        moscow_time -= 24
    
    return REMINDER_START_HOUR <= moscow_time < REMINDER_END_HOUR


async def send_reminders():
    """
    Фоновая задача: каждые 30 минут отправляет напоминания активным пользователям.
    Напоминания отправляются только в интервале с 10:00 до 21:00 по московскому времени.
    """
    while True:
        try:
            if is_reminder_time():
                # Получаем список активных пользователей
                users = database.get_all_users()
                
                if users:
                    # Отправляем сообщение каждому пользователю
                    for user_id in users:
                        try:
                            await bot.send_message(
                                user_id,
                                "Выпей воды!"
                            )
                            logger.info(f"Напоминание отправлено пользователю {user_id}")
                        except Exception as e:
                            # Если пользователь заблокировал бота или удалил чат,
                            # удаляем его из базы
                            logger.warning(
                                f"Не удалось отправить сообщение пользователю {user_id}: {e}"
                            )
                            database.remove_user(user_id)
                else:
                    logger.info("Нет активных пользователей для напоминаний")
            else:
                logger.info("Сейчас не время для напоминаний (вне интервала 10:00-21:00)")
                
        except Exception as e:
            logger.error(f"Ошибка в фоновой задаче: {e}")
        
        # Ждём 30 минут перед следующей проверкой
        await asyncio.sleep(REMINDER_INTERVAL * 60)


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    """
    Обработчик команды /start.
    Добавляет пользователя в список активных и отправляет приветственное сообщение.
    """
    user_id = message.from_user.id
    
    # Добавляем пользователя в базу данных
    added = database.add_user(user_id)
    
    if added:
        welcome_text = (
            "Привет! Я бот-напоминатор пить воду.\n\n"
            "Я буду напоминать тебе пить воду каждые 30 минут "
            "в период с 10:00 до 21:00 по московскому времени.\n\n"
            "Чтобы остановить напоминания, используй команду /stop."
        )
        logger.info(f"Пользователь {user_id} добавлен в список активных")
    else:
        welcome_text = (
            "Ты уже в моём списке активных пользователей!\n\n"
            "Я напоминаю пить воду каждые 30 минут с 10:00 до 21:00.\n\n"
            "Чтобы остановить напоминания, используй команду /stop."
        )
    
    await message.answer(welcome_text)


@router.message(Command("stop"))
async def cmd_stop(message: types.Message):
    """
    Обработчик команды /stop.
    Удаляет пользователя из списка активных.
    """
    user_id = message.from_user.id
    
    # Удаляем пользователя из базы данных
    removed = database.remove_user(user_id)
    
    if removed:
        stop_text = (
            "Ты удалён из списка активных пользователей.\n"
            "Напоминания больше приходить не будут.\n\n"
            "Чтобы снова получать напоминания, используй команду /start."
        )
        logger.info(f"Пользователь {user_id} удалён из списка активных")
    else:
        stop_text = (
            "Тебя и так нет в списке активных пользователей.\n\n"
            "Чтобы получать напоминания, используй команду /start."
        )
    
    await message.answer(stop_text)


async def main():
    """
    Главная функция запуска бота.
    """
    try:
        # Инициализация базы данных
        database.init_db()
        logger.info("База данных инициализирована")
        
        # Запуск фоновой задачи для напоминаний
        asyncio.create_task(send_reminders())
        logger.info("Фоновая задача напоминаний запущена")
        
        # Запуск бота (polling)
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"Критическая ошибка при запуске бота: {e}")
        exit(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен пользователем")
    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
