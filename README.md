```
drop schema s_sql_dds cascade;

set search_path to s_sql_dds, public;

docker compose start

docker compose exec app bash

python -m data_pipeline.main
```

# Clean

## PostgresSQL
```
docker-compose exec db psql -U postgres -d etl -c "
DROP SCHEMA s_sql_dds CASCADE;
VACUUM FULL;
"
```

## MySQL
```
docker-compose exec mysql mysql -u mysqluser -pmysqlpass dwh_mysql -e "
DROP TABLE IF EXISTS t_dm_stg_task, t_dm_task;
DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load;
"
```


# Check
## Postgres
```
docker compose exec db psql -U postgres -d etl
\dn
\dt s_sql_dds.*
SET search_path TO s_sql_dds, public;
SELECT COUNT(*) AS dm_rows FROM t_dm_task;
SELECT COUNT(*) AS v_rows  FROM v_dm_task;
```

## MySQL
```
docker compose exec mysql mysql -u mysqluser -pmysqlpass dwh_mysql -e "
SHOW TABLES;
SELECT COUNT(*) AS stg_rows FROM t_dm_stg_task;
SELECT COUNT(*) AS dm_rows  FROM t_dm_task;
SELECT task_sk, src_id, register_date 
FROM t_dm_stg_task 
ORDER BY task_sk 
LIMIT 5;
SELECT task_sk, src_id, register_date 
FROM t_dm_task 
ORDER BY task_sk 
LIMIT 5;
"
```