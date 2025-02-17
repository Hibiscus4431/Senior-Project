CREATE TABLE IF NOT EXISTS Questions (
    id SERIAL PRIMARY KEY,
    course_id INT DEFAULT NULL,
    textbook_id INT DEFAULT NULL,
    question_text TEXT NOT NULL,
    type VARCHAR(50) CHECK (type IN ('Multiple Choice', 'True/False', 'Short Answer', 'Essay')),
    true_false_answer BOOLEAN DEFAULT NULL,
    default_points INT DEFAULT 0,
    est_time INT,
    grading_instructions TEXT,
    owner_id INT NOT NULL,
    is_published BOOLEAN DEFAULT FALSE,
    attachment_id INT DEFAULT NULL,  
    source VARCHAR(50) CHECK (source IN ('manual', 'canvas_qti')) DEFAULT 'manual'
);

ALTER TABLE Questions 
DROP CONSTRAINT questions_type_check,  -- Drops the existing constraint

ALTER TABLE Questions
ADD COLUMN chapter_number INT DEFAULT NULL, 
ADD COLUMN section_number VARCHAR(50) DEFAULT NULL;

ALTER TABLE Questions 
ADD CONSTRAINT questions_type_check  -- Adds a new constraint
CHECK (type IN ('Multiple Choice', 'True/False', 'Short Answer', 'Essay', 'Matching', 'Fill in the Blank'));

