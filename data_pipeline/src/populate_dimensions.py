from data_pipeline.src.db import get_engine
from sqlalchemy import text


def populate_dimensions():
    """Заполняет dim_* таблицы из t_sql_source_structured."""
    engine = get_engine()

    populate_queries = [
        """
        INSERT INTO s_sql_dds.dim_name (name)
        SELECT DISTINCT name FROM s_sql_dds.t_sql_source_structured 
        WHERE name IS NOT NULL ON CONFLICT (name) DO NOTHING
        """,
        """
        INSERT INTO s_sql_dds.dim_country (name)
        SELECT DISTINCT country FROM s_sql_dds.t_sql_source_structured 
        WHERE country IS NOT NULL ON CONFLICT (name) DO NOTHING
        """,
        """
        INSERT INTO s_sql_dds.dim_city (name)
        SELECT DISTINCT city FROM s_sql_dds.t_sql_source_structured 
        WHERE city IS NOT NULL ON CONFLICT (name) DO NOTHING
        """,
        """
        INSERT INTO s_sql_dds.dim_gender (name)
        SELECT DISTINCT gender FROM s_sql_dds.t_sql_source_structured 
        WHERE gender IS NOT NULL ON CONFLICT (name) DO NOTHING
        """,
        """
        INSERT INTO s_sql_dds.dim_status (name)
        SELECT DISTINCT status FROM s_sql_dds.t_sql_source_structured 
        WHERE status IS NOT NULL ON CONFLICT (name) DO NOTHING
        """,
        """
        INSERT INTO s_sql_dds.dim_email (name)
        SELECT DISTINCT email FROM s_sql_dds.t_sql_source_structured 
        WHERE email IS NOT NULL ON CONFLICT (name) DO NOTHING
        """
    ]

    with engine.connect() as conn:
        conn.execute(text("SET search_path TO s_sql_dds, public"))
        for i, query in enumerate(populate_queries, 1):
            conn.execute(text(query))
            print(f"Populated dim #{i}")
        conn.commit()
        print("All dimensions populated")