import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from data_pipeline.src.config import settings

engine = create_engine(settings.url, future=True)
SessionLocal = sessionmaker(bind=engine, future=True)


def get_engine(db_type="pg"):
    from data_pipeline.src.config import settings
    if db_type == "pg":
        return create_engine(settings.url, future=True)
    elif db_type == "mysql":
        from data_pipeline.src.mysql_db import get_mysql_engine
        return get_mysql_engine()
    raise ValueError(f"Unknown db_type: {db_type}")


def get_session(db_type="pg"):
    if db_type == "pg":
        from data_pipeline.src.config import settings
        engine = create_engine(settings.url, future=True)
    elif db_type == "mysql":
        from data_pipeline.src.mysql_db import get_mysql_engine
        engine = get_mysql_engine()
    return sessionmaker(bind=engine, future=True)()


def run_sql_script(conn, sql_text: str):
    conn.execute(text(sql_text))
    conn.commit()


def call_fn_etl_data_load(start_date: str, end_date: str):
    with engine.connect() as conn:
        conn.execute(text("SET search_path TO s_sql_dds, public"))
        conn.execute(
            text("select s_sql_dds.fn_etl_data_load(:start, :end)"),
            {"start": start_date, "end": end_date}
        )
        conn.commit()


def call_fn_dm_data_load(start_date: str, end_date: str):
    with engine.connect() as conn:
        conn.execute(text("SET search_path TO s_sql_dds, public"))
        conn.execute(
            text("SELECT s_sql_dds.fn_dm_data_load(:start, :end)"),
            {"start": start_date, "end": end_date}
        )
        conn.commit()


def get_unstructured_data(limit: int = 10):
    session = get_session()
    try:
        result = session.execute(text(f"SELECT * FROM s_sql_dds.t_sql_source_unstructured LIMIT {limit}"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        total_count = session.execute(text("SELECT COUNT(*) FROM s_sql_dds.t_sql_source_unstructured")).scalar()
        return df, total_count
    finally:
        session.close()


def get_structured_data(limit: int = 10):
    session = get_session()
    try:
        result = session.execute(
            text(f"SELECT * FROM s_sql_dds.t_sql_source_structured ORDER BY register_date DESC LIMIT {limit}"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        total_count = session.execute(text("SELECT COUNT(*) FROM s_sql_dds.t_sql_source_structured")).scalar()
        return df, total_count
    finally:
        session.close()


def get_dm_data(limit: int = 10):
    session = get_session()
    try:
        result = session.execute(text(f"SELECT * FROM s_sql_dds.t_dm_task ORDER BY register_date DESC LIMIT {limit}"))
        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        total_count = session.execute(text("SELECT COUNT(*) FROM s_sql_dds.t_dm_task")).scalar()
        return df, total_count
    finally:
        session.close()


# checks
def call_fn_dq_checks_load(start_date: str, end_date: str):
    try:
        with get_engine("pg").connect() as conn:
            conn.execute(text("SET search_path TO s_sql_dds, public"))
            conn.execute(
                text("SELECT s_sql_dds.fn_dq_checks_load(:start, :end)"),
                {"start": start_date, "end": end_date}
            )
            conn.commit()
        return True, "Checks passed"
    except Exception as e:
        return False, f"Error DQ: {str(e)}"


def get_dq_results_last_run():
    session = get_session("pg")

    try:
        last_run = session.execute(
            text("""
                SELECT MAX(execution_date) as last_execution 
                FROM s_sql_dds.t_dq_check_results
            """)
        ).scalar()

        if not last_run:
            return pd.DataFrame(), "No data about checks"

        result = session.execute(
            text("""
                SELECT
                    check_type,
                    table_name,
                    status,
                    execution_date,
                    error_message
                FROM s_sql_dds.t_dq_check_results
                WHERE execution_date = :last_run
                ORDER BY check_type
            """),
            {"last_run": last_run}
        )

        df = pd.DataFrame(result.fetchall(), columns=result.keys())
        return df, f"Checks by {last_run}"
    finally:
        session.close()


def get_dq_summary():
    session = get_session("pg")
    try:
        result = session.execute(
            text("""
                SELECT 
                    COUNT(*) as total_checks,
                    COUNT(CASE WHEN status = 'passed' THEN 1 END) as passed,
                    COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed,
                    COUNT(CASE WHEN status = 'error' THEN 1 END) as errors
                FROM s_sql_dds.t_dq_check_results
            """)

        )
        row = result.fetchone()
        if row:
            return {
                'total_checks': row.total_checks or 0,
                'passed': row.passed or 0,
                'failed': row.failed or 0,
                'errors': row.errors or 0,
                'success_rate': round((row.passed or 0) / max(row.total_checks or 1, 1) * 100, 1)
            }

        return {}
    finally:
        session.close()


def check_dq_status():
    summary = get_dq_summary()

    if not summary:
        return False, "No data about checks"
    if summary.get('failed', 0) > 0 or summary.get('errors', 0) > 0:
        return False, f"Problems: {summary.get('failed')} failed, {summary.get('errors')} errors"

    return True, f"All checks passed ({summary.get('success_rate')}% successful)"

