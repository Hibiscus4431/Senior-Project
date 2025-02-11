CREATE TABLE IF NOT EXISTS Attachments_MetaData (
    id SERIAL PRIMARY KEY,
    attachment_id INT NOT NULL,
    reference_id INT NOT NULL,
    reference_type VARCHAR(20) CHECK (reference_type IN ('question', 'test')) NOT NULL
    );
