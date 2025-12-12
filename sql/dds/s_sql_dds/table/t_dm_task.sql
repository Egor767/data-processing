create table if not exists s_sql_dds.t_dm_task (
    task_sk       bigserial primary key,
    src_id        text not null,

    name_id       int,
    country_id    int,
    city_id       int,
    gender_id     int,
    email_id      int,
    status_id     int,

    age           integer,
    value         numeric(10,2),
    register_date date not null
);
