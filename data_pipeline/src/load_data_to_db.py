import pandas as pd
from sqlalchemy import text
from data_pipeline.src.db import get_engine
from data_pipeline.src.models import UserRecord


def load_data_to_db(records: list[UserRecord]):
    engine = get_engine()
    rows = [r.model_dump() for r in records]
    df = pd.DataFrame(rows)
    with engine.begin() as conn:
        conn.execute(text("set search_path to s_sql_dds, public"))
        conn.execute(text("truncate table s_sql_dds.t_sql_source_unstructured"))
        conn.execute(text("truncate table s_sql_dds.t_sql_source_structured"))
        df.to_sql("t_sql_source_unstructured", con=conn, schema="s_sql_dds", if_exists="append", index=False)
