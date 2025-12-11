import os
import pytest
from sqlalchemy import create_engine, text
from data_pipeline.src.config import settings, BASE_DIR


@pytest.fixture(scope="session")
def engine():
    e = create_engine(settings.url, future=True)
    return e


@pytest.fixture(scope="session", autouse=True)
def prepare_schema(engine):
    sql_dir = BASE_DIR / "sql" / "dds" / "s_sql_dds"

    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS s_sql_dds"))
        conn.execute(text("SET search_path TO s_sql_dds, public"))

        conn.execute(text((sql_dir / "table" / "t_sql_source_unstructured.sql").read_text()))
        conn.execute(text((sql_dir / "table" / "t_sql_source_structured.sql").read_text()))

        conn.execute(text((sql_dir / "function" / "fn_etl_data_load.sql").read_text()))

    yield

    # Cleanup
    with engine.begin() as conn:
        conn.execute(text("DROP SCHEMA IF EXISTS s_sql_dds CASCADE"))
