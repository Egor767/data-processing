from data_pipeline.src.export_to_mysql import mysql_etl
from data_pipeline.src.fill_dm_table import fill_dm_table
from data_pipeline.src.get_dataset import get_dataset
from data_pipeline.src.load_data_to_db import load_data_to_db
from data_pipeline.src.fill_structured_table import fill_structured_table
from data_pipeline.src.db import get_unstructured_data, get_structured_data, get_dm_data
from data_pipeline.src.populate_dimensions import populate_dimensions


def etl():
    count = 50
    date_start, date_end = '2023-01-01', '2025-01-01'

    print("Starting ETL...")
    records = get_dataset(n_rows=count, use_static_uuid=True)
    print(f"Records generated(count={len(records)})")
    print("Record[0]: ", records[0])
    load_data_to_db(records)

    print("Unstructured data from unstructured_table")
    df_raw, raw_count = get_unstructured_data(limit=count)
    print(df_raw.head(1))
    print(f"Get unstructured records (count={raw_count})")

    print(f"Filling structured_table({date_start}, {date_end})")
    fill_structured_table(date_start, date_end)
    print("ETL Done")

    print("Populating dimension tables...")
    populate_dimensions()

    print("Filling DM table...")
    fill_dm_table(date_start, date_end)

    print("Get structured data from table_structured")
    df, total_count = get_structured_data(limit=count)
    print(df.head(1))
    print(f"Get structured records (count={total_count})")

    print("Get DM data from t_dm_task")
    df_dm, dm_count = get_dm_data(limit=count)
    print(df_dm.head(1))
    print(f"DM records (count={dm_count})")
    print("DM Done")

    print("Starting MySQL ETL...")
    mysql_etl(date_start, date_end)
