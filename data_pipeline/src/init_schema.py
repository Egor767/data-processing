from sqlalchemy import text
from data_pipeline.src.db import get_engine
from .config import BASE_DIR


def init_schema():
    engine = get_engine()

    sql_dir = BASE_DIR / "sql" / "dds" / "s_sql_dds"

    ddl_order = [
        sql_dir / "table" / "t_sql_source_unstructured.sql",
        sql_dir / "table" / "t_sql_source_structured.sql",

        sql_dir / "table" / "t_dm.sql",

        sql_dir / "table" / "t_dm_task.sql",

        sql_dir / "function" / "fn_etl_data_load.sql",
        sql_dir / "function" / "fn_dm_data_load.sql",

        sql_dir / "view" / "v_dm_task.sql",
    ]

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS s_sql_dds"))
        conn.execute(text("SET search_path TO s_sql_dds, public"))
        conn.commit()
        print("Schema s_sql_dds created & search_path set")

        for sql_file in ddl_order:
            if sql_file.exists():
                sql_content = sql_file.read_text(encoding="utf-8")
                conn.execute(text(sql_content))
                conn.commit()
                print(f"Executed: {sql_file.name}")
            else:
                print(f"Warning: SQL file not found: {sql_file}")
