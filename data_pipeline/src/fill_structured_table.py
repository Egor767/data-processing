from datetime import date
from data_pipeline.src.db import call_fn_etl_data_load


def fill_structured_table(start_date: str | None = None, end_date: str | None = None):
    if not start_date or not end_date:
        end = date.today()
        start = end.replace(year=end.year - 1)
        start_date = start.isoformat()
        end_date = end.isoformat()

    call_fn_etl_data_load(start_date, end_date)