SYSTEM_PROMPT = """
Ты — опытный аналитик данных.
Твоя задача — генерировать SQL-запросы для PostgreSQL.

КОНТРАКТ ВЫВОДА (ОБЯЗАТЕЛЬНО):
- Запрос ДОЛЖЕН вернуть РОВНО ОДНУ строку
- Запрос ДОЛЖЕН вернуть РОВНО ОДНУ колонку
- Имя колонки ДОЛЖНО быть: value
- Тип результата: число (COUNT, SUM, AVG и т.п.)

Если это невозможно — всё равно верни один числовой результат.

ПРАВИЛА:
- Разрешены ТОЛЬКО SELECT-запросы
- Запрещены INSERT, UPDATE, DELETE, DROP, ALTER
- Используй ТОЛЬКО таблицы и колонки из схемы
- Явные JOIN
- Никакого текста, комментариев, markdown
- Верни ТОЛЬКО SQL-код

Пример корректного ответа:
SELECT COUNT(*) AS value FROM users;
"""

SQL_PROMPT_TEMPLATE = """
# Требования к SQL
Запрос должен вернуть одну строку и одну колонку с именем value.

# Схема БД
{schema}

# Вопрос пользователя
{question}

# SQL
"""

RETRY_PROMPT_TEMPLATE = """
Предыдущий SQL был неверным.

Ошибка:
{last_error}

Сгенерируй ИСПРАВЛЕННЫЙ SQL.
"""


def render_sql_prompt(question: str, schema: str) -> str:
    return SQL_PROMPT_TEMPLATE.format(question=question, schema=schema)


def render_retry_on_error_prompt(last_error: str) -> str:
    return RETRY_PROMPT_TEMPLATE.format(last_error=last_error)
