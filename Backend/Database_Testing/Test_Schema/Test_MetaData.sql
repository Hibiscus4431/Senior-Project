CREATE TABLE IF NOT EXISTS Test_MetaData (
    test_id INT NOT NULL,
    question_id INT NOT NULL,
    points INT DEFAULT 0,
    order_num INT NOT NULL,
    PRIMARY KEY (test_id, question_id)
);
