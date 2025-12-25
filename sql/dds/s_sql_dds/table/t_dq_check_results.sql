drop table if exists s_sql_dds.t_dq_check_results;
create table s_sql_dds.t_dq_check_results (
  check_id serial primary key,
  check_type varchar(50) not null,
  table_name varchar(100) not null,
  execution_date timestamp(6) default current_timestamp,
  status varchar(20) not null,
  records_checked bigint,
  records_failed bigint default 0,
  error_message text,
  details jsonb
);
