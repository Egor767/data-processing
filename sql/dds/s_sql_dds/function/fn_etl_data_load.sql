create or replace function s_sql_dds.fn_etl_data_load(start_date date, end_date date)
returns void language plpgsql as
$$
declare
    valid_countries text[] := array['RU','US','DE','GB','FR','JP','CN'];
    valid_genders text[] := array['male','female'];
    valid_statuses text[] := array['new','active','deleted'];
begin
    with prepared as (
        select
            -- ID: пустые → UUID, trim()
            coalesce(nullif(trim(t.id), ''), gen_random_uuid()::text)::text as id_val,

            -- name: пустые → 'unknown'
            coalesce(nullif(trim(t.name), ''), 'unknown')::text as name_val,

            -- age: только 10-100, иначе NULL
            case
                when t.age is null then null
                when (t.age::integer) between 10 and 100 then t.age::integer
                else null
            end as age_val,

            -- gender: только из справочника → NULL
            case
                when lower(trim(t.gender)) = any(valid_genders)
                then lower(trim(t.gender))
                else null
            end as gender_val,

            -- status: только из справочника → NULL
            case
                when lower(trim(t.status)) = any(valid_statuses)
                then lower(trim(t.status))
                else null
            end as status_val,

            -- value: отрицательные/outliers → NULL
            case
                when t.value is null then null
                when (t.value::numeric) >= 0 and (t.value::numeric) <= 1000 then t.value::numeric
                else null
            end as value_val,

            -- country: только коды → 'unknown'
            case
                when t.country is not null
                     and trim(t.country) <> ''
                     and upper(trim(t.country)) = any(valid_countries)
                then upper(trim(t.country))
                else 'unknown'
            end as country_val,

            -- city: пустые → 'unknown'
            coalesce(nullif(trim(t.city), ''), 'unknown')::text as city_val,

            -- register_date: NULL → current_date
            coalesce((t.register_date::date), current_date) as register_date_val,

            -- email: базовая валидация → lower(trim()) или 'unknown'
            coalesce(
                (case
                    when t.email is not null
                         and position('@' in t.email) > 1
                         and position('.' in substring(t.email from position('@' in t.email) + 1)) > 1
                    then lower(trim(t.email))
                    else null
                end),
                'unknown'
            ) as email_val

        from s_sql_dds.t_sql_source_unstructured t
        where coalesce((t.register_date::date), current_date) between start_date and end_date
    ),
    dedup as (
        -- одна строка на id (последняя по register_date)
        select distinct on (id_val)
            id_val, name_val, age_val, gender_val, status_val, value_val,
            country_val, city_val, register_date_val, email_val
        from prepared
        order by id_val, register_date_val desc
    )
    insert into s_sql_dds.t_sql_source_structured (
        id, name, age, gender, status, value, country, city, register_date, email
    )
    select
        id_val, name_val, age_val, gender_val, status_val, value_val,
        country_val, city_val, register_date_val, email_val
    from dedup
    on conflict (id) do update set
        name = excluded.name,
        age = excluded.age,
        gender = excluded.gender,
        status = excluded.status,
        value = excluded.value,
        country = excluded.country,
        city = excluded.city,
        register_date = excluded.register_date,
        email = excluded.email;
end;
$$;