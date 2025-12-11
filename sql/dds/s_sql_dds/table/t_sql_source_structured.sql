create table if not exists s_sql_dds.t_sql_source_structured (
    id text primary key,
    name text not null,
    country text,
    city text,
    age integer check (age between 10 and 100),
    gender text check (gender in ('male', 'female')),
    email text,
    status text check (status in ('new', 'active', 'deleted')),
    value numeric(10,2) check (value >= 0 and value <= 1000),
    register_date date not null
);