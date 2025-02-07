CREATE TABLE Test_MetaData (
    test_id INT NOT NULL,
    question_id INT NOT NULL,
    points INT DEFAULT 0,
    order_num NOT NULL,
    PRIMARY KEY (test_id, question_id)
);
