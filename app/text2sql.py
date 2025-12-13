import logging
from typing import Any

from langchain_gigachat import GigaChat
from sqlalchemy import Result, text
from tabulate import tabulate

from app.db import session_maker
from app.prompts import PROMPT_TEMPLATE, SYSTEM_PROMPT
from app.render_db import db_schema
from app.settings import settings
from app.validate_sql import is_read_only_sql

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

logger = logging.getLogger(__name__)

llm = GigaChat(
    credentials=settings.GIGACHAT_API,
    verify_ssl_certs=False,
)


def render_prompt(question: str, schema: str) -> str:
    return PROMPT_TEMPLATE.format(question=question, schema=schema)


def ask_llm(question: str) -> str:
    prompt = render_prompt(question, db_schema)

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
    rows = result.fetchall()

    if not rows:
        return "(0 rows)\n"

    column_names = result.keys()

    table_data = [list(row) for row in rows]

    return tabulate(
        table_data,
        headers=column_names,
        tablefmt="grid",
        showindex=False,
    )


def text2sql(question: str):
    sql = ask_llm(question)

    logger.info("Generated SQL: %s", sql)

    if not is_read_only_sql(sql):
        return "Произошла ошибка. Попробуйте ещё раз."

    session = session_maker()
    records = session.execute(text(sql))
    logger.info(f"Fetched {len(records.all())} rows from db")
    return format_sqlalchemy_result(records)
