CREATE TABLE IF NOT EXISTS t_dm_task (
    task_sk BIGINT AUTO_INCREMENT PRIMARY KEY,
    src_id VARCHAR(36) NOT NULL,
    name_id INT,
    country_id INT,
    city_id INT,
    gender_id INT,
    email_id INT,
    status_id INT,
    age INT,
    value DECIMAL(10,2),
    register_date DATE NOT NULL,
    UNIQUE KEY unique_fact (src_id, register_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;