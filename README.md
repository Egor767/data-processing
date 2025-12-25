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

docker-compose exec db psql -U postgres -d etl -c "
-- 1. Счетчик ДО
SELECT 'BEFORE' as step, COUNT(*) as dq_count FROM s_sql_dds.t_dq_check_results;

-- 2. ПРАВИЛЬНЫЙ INSERT со ВСЕМИ NOT NULL полями
INSERT INTO s_sql_dds.t_dm_task (task_sk, src_id, register_date) 
VALUES (888, 'trigger-test-123', CURRENT_DATE);

-- 3. Счетчик ПОСЛЕ (должно +5!)
SELECT 'AFTER' as step, COUNT(*) as dq_count FROM s_sql_dds.t_dq_check_results;

-- 4. Последние 5 проверок (должны быть свежие!)
SELECT execution_date, check_type, status 
FROM s_sql_dds.t_dq_check_results 
ORDER BY execution_date DESC LIMIT 20;
"


