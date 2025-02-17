CREATE TABLE IF NOT EXISTS Textbook (
    textbook_id SERIAL PRIMARY KEY,
    textbook_title VARCHAR(255) NOT NULL,
    textbook_author VARCHAR(255) NOT NULL,
    textbook_version VARCHAR(255) NOT NULL,
    textbook_isbn VARCHAR(255) NOT NULL
);

-- Adding publisher_id to the Textbook table (each textbook has a publisher)
ALTER TABLE Textbook
ADD COLUMN publisher_id INT;