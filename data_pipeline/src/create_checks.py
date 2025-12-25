from data_pipeline.src.db import call_fn_dq_checks_load


def create_checks(date_start="1900-01-01", date_end="2100-12-31"):
    return call_fn_dq_checks_load(date_start, date_end)
