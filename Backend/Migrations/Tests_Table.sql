CREATE TABLE TESTS(
    tests_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    template_id INT,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) CHECK (status IN ('Draft', 'Final', 'Published')),
    points_total INT DEFAULT 0,
    estimated_time INT, 
    filename VARCHAR(255),
    test_instrucutions TEXT
    CHECK (status <> 'published' OR filename IS NOT NULL) 
    );