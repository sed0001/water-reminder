"""
Модуль для работы с базой данных SQLite.
Хранит информацию об активных пользователях бота.
"""
import sqlite3
from typing import List, Optional


DATABASE_NAME = "water_reminder.db"


def get_connection() -> sqlite3.Connection:
    """Устанавливает соединение с базой данных."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Позволяет обращаться к полям по имени
    return conn


def init_db() -> None:
    """
    Инициализирует базу данных.
    Создаёт таблицу users, если она ещё не существует.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY
        )
    """)
    
    conn.commit()
    conn.close()


def add_user(user_id: int) -> bool:
    """
    Добавляет пользователя в список активных.
    
    Args:
        user_id: ID пользователя Telegram.
    
    Returns:
        True, если пользователь добавлен; False, если уже был в базе.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Проверяем, существует ли пользователь
    cursor.execute("SELECT 1 FROM users WHERE user_id = ?", (user_id,))
    exists = cursor.fetchone() is not None
    
    if not exists:
        cursor.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()
    
    conn.close()
    return not exists


def remove_user(user_id: int) -> bool:
    """
    Удаляет пользователя из списка активных.
    
    Args:
        user_id: ID пользователя Telegram.
    
    Returns:
        True, если пользователь был удалён; False, если его не было в базе.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    return deleted


def get_all_users() -> List[int]:
    """
    Возвращает список всех активных пользователей.
    
    Returns:
        Список ID пользователей.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT user_id FROM users")
    users = [row["user_id"] for row in cursor.fetchall()]
    
    conn.close()
    return users
