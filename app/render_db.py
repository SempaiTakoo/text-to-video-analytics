import sqlalchemy


def render_column_description(column: sqlalchemy.Column) -> str:
    pk = ", PK" if column.primary_key else ""
    fks = [f"{fk.column.table.name}.{fk.column.name}" for fk in column.foreign_keys]
    fk = ", FK -> " + ", ".join(fks) if fks else ""
    return f"- {column.name} ({column.type}{pk}{fk}) - {column.comment or 'No description'}"


def render_table_description(table: sqlalchemy.Table) -> str:
    header = f"Table: {table.name} — {table.comment or 'No description'}"
    columns = "\n".join(render_column_description(column) for column in table.columns)
    return f"{header}\nColumns:\n{columns}"


def render_db_description(metadata: sqlalchemy.MetaData) -> str:
    return "\n\n".join(
        render_table_description(table) for table in metadata.sorted_tables
    )
