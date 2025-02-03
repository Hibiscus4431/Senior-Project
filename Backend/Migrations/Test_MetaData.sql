CREATE TABLE Test_MetaData (
    Metadata_id SERIAL PRIMARY KEY,
    test_id INT NOT NULL,
    question_id INT NOT NULL,
    points INT DEFAULT 0,
    order_num INT
);