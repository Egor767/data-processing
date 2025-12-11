create schema if not exists s_sql_dds;

create table if not exists s_sql_dds.t_sql_source_unstructured (
    id text,
    name text,
    country text,
    city text,
    age integer,
    gender text,
    email text,
    status text,
    value numeric(10,2),
    register_date date
);