create or replace view s_sql_dds.v_dm_task as
select
    task_sk,
    src_id,
    name_id,
    country_id,
    city_id,
    gender_id,
    email_id,
    status_id,
    age,
    value,
    register_date
from s_sql_dds.t_dm_task;