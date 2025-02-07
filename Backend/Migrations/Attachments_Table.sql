CREATE TABLE Attachments (
    attachments_id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    filepath VARCHAR(255) NOT NULL,
);
