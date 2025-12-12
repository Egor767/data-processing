DROP PROCEDURE IF EXISTS fn_dm_data_stg_to_dm_load;

CREATE PROCEDURE fn_dm_data_stg_to_dm_load(IN start_dt DATE, IN end_dt DATE)
BEGIN
    DELETE FROM t_dm_task WHERE register_date BETWEEN start_dt AND end_dt;

    INSERT INTO t_dm_task (
        src_id, name_id, country_id, city_id, gender_id,
        email_id, status_id, age, value, register_date
    )
    SELECT
        src_id, name_id, country_id, city_id, gender_id,
        email_id, status_id, age, value, register_date
    FROM t_dm_stg_task
    WHERE register_date BETWEEN start_dt AND end_dt;
END;