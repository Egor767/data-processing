from sqlalchemy import text

from data_pipeline.src.mysql_db import (
    init_mysql_schema,
    export_v_dm_to_mysql_stg,
    get_mysql_engine,
)


def mysql_etl(start_date: str, end_date: str):
    print("Initializing MySQL schema...")
    init_mysql_schema()

    print("Exporting v_dm_task → t_dm_stg_task...")
    export_v_dm_to_mysql_stg()

    print("Calling MySQL fn_dm_data_stg_to_dm_load...")
    with get_mysql_engine().connect() as conn:
        conn.execute(
            text("CALL fn_dm_data_stg_to_dm_load(:start, :end)"),
            {"start": start_date, "end": end_date},
        )
        conn.commit()

    print("MySQL ETL Done!")
