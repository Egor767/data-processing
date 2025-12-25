from sqlalchemy import text
from data_pipeline.src.db import get_engine
from .config import BASE_DIR


def init_schema():
    engine = get_engine()
    sql_dir = BASE_DIR / "sql" / "dds" / "s_sql_dds"

    ddl_order = [
        # table
        sql_dir / "table" / "t_sql_source_unstructured.sql",
        sql_dir / "table" / "t_sql_source_structured.sql",
        sql_dir / "table" / "t_dm.sql",
        sql_dir / "table" / "t_dm_task.sql",
        sql_dir / "table" / "t_dq_check_results.sql",

        # function
        sql_dir / "function" / "fn_etl_data_load.sql",
        sql_dir / "function" / "fn_dm_data_load.sql",
        sql_dir / "function" / "fn_dq_checks_load.sql",

        # view
        sql_dir / "view" / "v_dm_task.sql",

        # trigger
        sql_dir / "triggers" / "t_dq_trigger.sql"
    ]

    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS s_sql_dds"))
        conn.execute(text("SET search_path TO s_sql_dds, public"))
        conn.commit()

        for sql_file in ddl_order:
            if sql_file.exists():
                sql_content = sql_file.read_text(encoding="utf-8")
                conn.execute(text(sql_content))
                conn.commit()
                print(f"Executed: {sql_file.name}")
