from sqlalchemy import text
from data_pipeline.src.get_dataset import get_dataset
from data_pipeline.src.load_data_to_db import load_data_to_db
from data_pipeline.src.db import call_fn_etl_data_load


def test_etl_end_to_end(engine):
    records = get_dataset(10)

    load_data_to_db(records)

    start = "2000-01-01"
    end = "2100-01-01"
    call_fn_etl_data_load(start, end)

    with engine.connect() as conn:
        conn.execute(text("SET search_path TO s_sql_dds, public"))

        unstructured_count = conn.execute(
            text("SELECT count(*) FROM t_sql_source_unstructured")
        ).scalar()
        assert unstructured_count == 10

        structured_count = conn.execute(
            text("SELECT count(*) FROM t_sql_source_structured")
        ).scalar()
        assert 0 < structured_count <= 10

        valid_age = conn.execute(
            text("SELECT count(*) FROM t_sql_source_structured WHERE age BETWEEN 10 AND 100 OR age IS NULL")
        ).scalar()
        assert valid_age == structured_count

