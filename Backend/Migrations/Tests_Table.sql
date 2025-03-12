CREATE TABLE IF NOT EXISTS TESTS(
    tests_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    template_id INT,
    user_id UUID NOT NULL,
    name VARCHAR(255) NOT NULL,
    status VARCHAR(50) DEFAULT 'Draft' CHECK (status IN ('Draft', 'Final', 'Published')),
    points_total INT DEFAULT 0 CHECK (points_total >= 0),
    estimated_time INT CHECK (estimated_time IS NULL or estimated_time > 0), 
    filename VARCHAR(255),
    test_instrucutions TEXT,
    UNIQUE (name, course_id),
    CHECK (status <> 'published' OR filename IS NOT NULL) 
    );
