CREATE TABLE Templates (
    template_id SERIAL PRIMARY KEY,
    template_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(255) NOT NULL,
);