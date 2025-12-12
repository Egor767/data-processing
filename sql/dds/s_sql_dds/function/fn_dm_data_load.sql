create or replace function s_sql_dds.fn_dm_data_load(start_dt date, end_dt date)
returns void
language plpgsql
as
$$
begin
    insert into s_sql_dds.t_dm_task (
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
    )
    select
        s.id as src_id,
        n.id  as name_id,
        c.id  as country_id,
        ci.id as city_id,
        g.id  as gender_id,
        e.id  as email_id,
        st.id as status_id,
        s.age,
        s.value,
        s.register_date
    from s_sql_dds.t_sql_source_structured s
    left join s_sql_dds.dim_name    n  on n.name  = s.name
    left join s_sql_dds.dim_country c  on c.name  = s.country
    left join s_sql_dds.dim_city    ci on ci.name = s.city
    left join s_sql_dds.dim_gender  g  on g.name  = s.gender
    left join s_sql_dds.dim_email   e  on e.name  = s.email
    left join s_sql_dds.dim_status  st on st.name = s.status
    where s.register_date between start_dt and end_dt
    on conflict do nothing;
end;
$$;
