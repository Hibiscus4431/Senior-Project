CREATE TABLE Questions (
    question_id SERIAL PRIMARY KEY,
    course_id INT NOT NULL,
    question_text TEXT NOT NULL
    type VARCHAR(50) CHECK (type IN ('Multiple Choice', 'True/False', 'Short Answer', 'Essay')),
    options JSON,
    correct_answer TEXT,
    default_points INT DEFAULT 0,
    est_time INT,
    grading_instructions TEXT,
    owner_id INT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    attachment_id INT  
    source VARCHAR(50) CHECK (source IN ('manual', 'canvas_qti')) DEFAULT 'manual'
);
