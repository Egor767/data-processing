create or replace function s_sql_dds.fn_dq_checks_load(start_dt date, end_dt date)
returns void language plpgsql as
$$
begin
    delete from s_sql_dds.t_dq_check_results
    where execution_date >= start_dt and execution_date < end_dt::date + interval '1 day';

    insert into s_sql_dds.t_dq_check_results (check_type, table_name, status, records_checked, records_failed, details)
    with structured_sum as (
        select sum(value) as total_value from s_sql_dds.t_sql_source_structured
        where register_date between start_dt and end_dt
    ),
    dm_sum as (
        select sum(value) as total_value from s_sql_dds.t_dm_task
        where register_date between start_dt and end_dt
    )
    select
        'correctness' as check_type,
        't_sql_source_structured vs t_dm_task' as table_name,
        case when abs((s.total_value - d.total_value)) / nullif(s.total_value, 0) < 0.01
             then 'passed' else 'failed' end as status,
        (select count(*) from s_sql_dds.t_sql_source_structured where register_date between start_dt and end_dt),
        0 as records_failed,
        jsonb_build_object('structured_sum', s.total_value, 'dm_sum', d.total_value) as details
    from structured_sum s cross join dm_sum d;

    insert into s_sql_dds.t_dq_check_results (check_type, table_name, status, records_checked, records_failed, details)
    with stats as (
        select
            count(*) as total,
            count(name_id) as name_ok,
            count(country_id) as country_ok,
            count(city_id) as city_ok
        from s_sql_dds.t_dm_task
        where register_date between start_dt and end_dt
    )
    select
        'completeness',
        't_dm_task',
        case when (name_ok + country_ok + city_ok)::numeric / (total * 3) > 0.95 then 'passed' else 'failed' end,
        total,
        (total * 3 - (name_ok + country_ok + city_ok))::bigint as records_failed,
        jsonb_build_object(
            'name_null_pct', round((1.0::numeric - name_ok::numeric/total::numeric), 4),
            'country_null_pct', round((1.0::numeric - country_ok::numeric/total::numeric), 4),
            'city_null_pct', round((1.0::numeric - city_ok::numeric/total::numeric), 4)
        ) as details
    from stats;

    insert into s_sql_dds.t_dq_check_results (check_type, table_name, status, records_checked, records_failed)
    with duplicates as (
        select count(*) as dup_count
        from (select src_id, register_date, count(*)
              from s_sql_dds.t_dm_task
              where register_date between start_dt and end_dt
              group by src_id, register_date
              having count(*) > 1) t
    )
    select
        'uniqueness',
        't_dm_task',
        case when coalesce(dup_count, 0) = 0 then 'passed' else 'failed' end,
        (select count(*) from s_sql_dds.t_dm_task where register_date between start_dt and end_dt),
        coalesce(dup_count, 0)
    from duplicates;

    insert into s_sql_dds.t_dq_check_results (check_type, table_name, status, records_checked, records_failed)
    select
        'validity',
        't_dm_task.age',
        case when invalid_count = 0 then 'passed' else 'failed' end,
        total_count,
        invalid_count
    from (
        select
            count(*) as total_count,
            sum(case when age is null or age < 10 or age > 100 then 1 else 0 end) as invalid_count
        from s_sql_dds.t_dm_task
        where register_date between start_dt and end_dt
    ) t;

    insert into s_sql_dds.t_dq_check_results (check_type, table_name, status, records_checked, records_failed)
    with violations as (
        select count(*) as violation_count
        from s_sql_dds.t_dm_task t
        left join s_sql_dds.dim_status st on t.status_id = st.id
        where t.register_date between start_dt and end_dt
          and (st.name = 'active' or st.name is null)
          and (t.value <= 0 or t.value is null)
    )
    select
        'consistency',
        't_dm_task.value_for_active',
        case when coalesce(violation_count, 0) = 0 then 'passed' else 'failed' end,
        coalesce((select count(*) from s_sql_dds.t_dm_task t
                  left join s_sql_dds.dim_status st on t.status_id = st.id
                  where t.register_date between start_dt and end_dt
                    and (st.name = 'active' or st.name is null)), 0),
        coalesce(violation_count, 0)
    from violations;

end;
$$;
