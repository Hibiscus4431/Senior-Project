CREATE TABLE IF NOT EXISTS Textbook (
    textbook_id SERIAL PRIMARY KEY,
    textbook_title VARCHAR(255) NOT NULL,
    textbook_author VARCHAR(255) NOT NULL,
    textbook_version VARCHAR(255) NOT NULL,
    textbook_isbn VARCHAR(255) NOT NULL,
    publisher_id INT
);

/*
Do not need this line anymore becasue i deleted the table from supabase and we can now add this row without messing up the flow
-- Adding publisher_id to the Textbook table (each textbook has a publisher)
ALTER TABLE Textbook
ADD COLUMN publisher_id INT;
*/
