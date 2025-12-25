CREATE TABLE IF NOT EXISTS t_dm_task (
    task_sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    src_id VARCHAR(36) NOT NULL,
    name_id INT NULL,
    country_id INT NULL,
    city_id INT NULL,
    gender_id INT NULL,
    email_id INT NULL,
    status_id INT NULL,
    age INT NULL,
    value DECIMAL(10,2) NULL,
    register_date DATE NOT NULL,
    UNIQUE KEY unique_fact (src_id, register_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;