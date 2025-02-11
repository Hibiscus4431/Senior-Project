CREATE TABLE Answer_Key (
    answer_key_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
);