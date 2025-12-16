import sqlglot
import sqlglot.errors

FORBIDDEN_EXPRESSIONS = (
    sqlglot.exp.Insert,
    sqlglot.exp.Update,
    sqlglot.exp.Delete,
    sqlglot.exp.Merge,
    sqlglot.exp.Drop,
    sqlglot.exp.Create,
    sqlglot.exp.Alter,
    sqlglot.exp.TruncateTable,
    sqlglot.exp.Grant,
    sqlglot.exp.Revoke,
)


def is_read_only_sql(sql: str, dialect: str = "postgres") -> bool:
    try:
        parsed = sqlglot.parse_one(sql, read=dialect)
    except sqlglot.errors.ParseError:
        return False

    if any(isinstance(node, FORBIDDEN_EXPRESSIONS) for node in parsed.walk()):
        return False

    return isinstance(parsed, (sqlglot.exp.Select, sqlglot.exp.With))
