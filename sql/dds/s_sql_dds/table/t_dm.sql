create table if not exists s_sql_dds.dim_name (
    id serial primary key,
    name varchar not null unique
);

create table if not exists s_sql_dds.dim_country (
    id serial primary key,
    name varchar not null unique
);

create table if not exists s_sql_dds.dim_city (
    id serial primary key,
    name varchar not null unique
);

create table if not exists s_sql_dds.dim_gender (
    id serial primary key,
    name varchar not null unique
);

create table if not exists s_sql_dds.dim_status (
    id serial primary key,
    name varchar not null unique
);

create table if not exists s_sql_dds.dim_email (
    id serial primary key,
    name varchar not null unique
);

insert into s_sql_dds.dim_name (name)
select distinct name
from s_sql_dds.t_sql_source_structured
where name is not null
on conflict (name) do nothing;

insert into s_sql_dds.dim_country (name)
select distinct country
from s_sql_dds.t_sql_source_structured
where country is not null
on conflict (name) do nothing;

insert into s_sql_dds.dim_city (name)
select distinct city
from s_sql_dds.t_sql_source_structured
where city is not null
on conflict (name) do nothing;

insert into s_sql_dds.dim_gender (name)
select distinct gender
from s_sql_dds.t_sql_source_structured
where gender is not null
on conflict (name) do nothing;

insert into s_sql_dds.dim_status (name)
select distinct status
from s_sql_dds.t_sql_source_structured
where status is not null
on conflict (name) do nothing;

insert into s_sql_dds.dim_email (name)
select distinct email
from s_sql_dds.t_sql_source_structured
where email is not null
on conflict (name) do nothing;