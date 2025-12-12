from data_pipeline.src.db import call_fn_dm_data_load


def fill_dm_table(start_date: str, end_date: str):
    print(f"Filling DM table ({start_date}, {end_date})")
    call_fn_dm_data_load(start_date, end_date)
    print("DM table filled")