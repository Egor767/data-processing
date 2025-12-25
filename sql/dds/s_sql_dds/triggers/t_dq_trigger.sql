CREATE OR REPLACE FUNCTION trigger_dq_check()
RETURNS TRIGGER AS $$
BEGIN
    PERFORM s_sql_dds.fn_dq_checks_load('2023-01-01'::date, CURRENT_DATE);
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS dq_check_trigger ON s_sql_dds.t_dm_task;
CREATE TRIGGER dq_check_trigger
    AFTER INSERT ON s_sql_dds.t_dm_task
    FOR EACH STATEMENT
    EXECUTE FUNCTION trigger_dq_check();
