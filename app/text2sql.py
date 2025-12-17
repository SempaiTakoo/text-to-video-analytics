import logging
from typing import Any

from langchain_gigachat import GigaChat
from sqlalchemy import Result, text
from sqlalchemy.exc import ProgrammingError

from app.db import session_maker
from app.prompts import (
    SYSTEM_PROMPT,
    render_retry_on_error_prompt,
    render_sql_prompt,
)
from app.render_db import db_schema
from app.settings import settings
from app.validate_sql import is_read_only_sql

logger = logging.getLogger(__name__)

DEFAULT_ERROR_MESSAGE = "Произошла ошибка. Попробуйте ещё раз"
DEFAULT_MAX_ATTEMPTS = 3

llm = GigaChat(
    credentials=settings.GIGACHAT_API,
    verify_ssl_certs=False,
)


def ask_llm(prompt: str) -> str:
    response = llm.invoke(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )
    tokens: int = response.response_metadata["token_usage"]["total_tokens"]
    logger.info(f"{tokens} tokens burned")
    return response.text()


def format_sqlalchemy_result(result: Result[Any]) -> str:
    answer = result.one_or_none()
    if answer is None or len(answer) != 1:
        return DEFAULT_ERROR_MESSAGE
    return str(answer[0])


def text_to_simpte_aggregate_sql(
    question: str,
    max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    database_schema: str = db_schema,
) -> str:
    last_error: str | None = None

    for i in range(1, max_attempts + 1):
        logger.info(f"Attempt to generate sql: {i}")

        prompt = render_sql_prompt(
            question=(
                question
                if last_error is None
                else render_retry_on_error_prompt(last_error)
            ),
            schema=database_schema,
        )

        logger.info(f"Using prompt: {prompt}")

        sql = ask_llm(prompt)

        logger.info("Generated SQL: %s", sql)

        if is_read_only_sql(sql):
            break
    else:
        logger.error(f"After {max_attempts} attempts failed to generated")
        return "Не удалось сгенерировать. Попробуйте ещё раз."

    return sql


def fetch_and_format_aggregate_result(sql: str) -> str:
    with session_maker() as session:
        try:
            records = session.execute(text(sql))
        except ProgrammingError:
            logger.exception("Exception handled during DB query")
            return DEFAULT_ERROR_MESSAGE

    return format_sqlalchemy_result(records)
