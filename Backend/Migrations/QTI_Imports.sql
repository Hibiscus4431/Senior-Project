CREATE TABLE QTI_Imports (
    import_id SERIAL PRIMARY KEY,
    file_path VARCHAR(255) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('pending', 'processed', 'failed'))
    owner_id INT NOT NULL
    test_id INT NOT NULL
    );
