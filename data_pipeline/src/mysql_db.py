import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from data_pipeline.src.config import mysql_settings, BASE_DIR
from data_pipeline.src.db import get_engine

mysql_engine = create_engine(mysql_settings.url, future=True)
MysqlSessionLocal = sessionmaker(bind=mysql_engine, future=True)


def get_mysql_engine():
    return mysql_engine


def get_mysql_session():
    return MysqlSessionLocal()


def init_mysql_schema():
    mysql_dir = BASE_DIR / "sql" / "dm" / "s_sql_dm"

    table_files = [
        mysql_dir / "table" / "t_dm_stg_task.sql",
        mysql_dir / "table" / "t_dm_task.sql",
    ]

    with get_mysql_engine().connect() as conn:
        for sql_file in table_files:
            if sql_file.exists():
                sql_content = sql_file.read_text(encoding="utf-8")
                conn.execute(text(sql_content))
                conn.commit()
                print(f"MySQL: Executed {sql_file.name}")

    with get_mysql_engine().connect() as conn:
        conn.execute(text("DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load"))
        conn.commit()

        conn.execute(text("""
            CREATE PROCEDURE fn_dm_data_stg_to_dm_load(IN start_dt DATE, IN end_dt DATE)
            BEGIN
                DELETE FROM t_dm_task WHERE register_date BETWEEN start_dt AND end_dt;
                INSERT INTO t_dm_task (
                    src_id, name_id, country_id, city_id, gender_id, 
                    email_id, status_id, age, value, register_date
                )
                SELECT src_id, name_id, country_id, city_id, gender_id, 
                       email_id, status_id, age, value, register_date
                FROM t_dm_stg_task
                WHERE register_date BETWEEN start_dt AND end_dt;
            END
        """))
        conn.commit()
        print("MySQL: Created fn_dm_data_stg_to_dm_load")

    print("MySQL schema fully initialized")


def export_v_dm_to_mysql_stg():
    pg_engine = get_engine()
    query = text("SELECT * FROM s_sql_dds.v_dm_task")
    pg_df = pd.read_sql(query, pg_engine)

    if 'task_sk' in pg_df.columns:
        pg_df = pg_df.drop(columns=['task_sk'])

    with get_mysql_engine().connect() as conn:
        conn.execute(text("TRUNCATE TABLE t_dm_stg_task"))
        conn.commit()
        print("Cleared t_dm_stg_task")

    pg_df.to_sql(
        "t_dm_stg_task",
        get_mysql_engine(),
        if_exists="append",
        index=False,
        method="multi"
    )
    print(f"Exported {len(pg_df)} rows to MySQL t_dm_stg_task")